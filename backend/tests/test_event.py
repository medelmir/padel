from datetime import date, time, timedelta

import pytest
from fastapi import status
from pydantic import ValidationError

from app.core.security import create_access_token
from app.models.models import Player, Team, Event, Match
from app.schemas.event import EventCreate, MatchInEventCreate


def auth_headers(user):
    token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role}
    )
    return {"Authorization": f"Bearer {token}"}


def create_player(
    db_session,
    first_name,
    last_name,
    company,
    license_number,
):
    player = Player(
        first_name=first_name,
        last_name=last_name,
        company=company,
        license_number=license_number,
    )
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)
    return player


def create_team(db_session, company, player1, player2):
    team = Team(company=company, player1_id=player1.id, player2_id=player2.id)
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    return team


def create_two_teams(db_session):
    player1 = create_player(db_session, "Alex", "Stone", "Alpha", "L100001")
    player2 = create_player(db_session, "Blake", "Stone", "Alpha", "L100002")
    player3 = create_player(db_session, "Casey", "Vale", "Bravo", "L100003")
    player4 = create_player(db_session, "Dana", "Vale", "Bravo", "L100004")
    team1 = create_team(db_session, "Alpha", player1, player2)
    team2 = create_team(db_session, "Bravo", player3, player4)
    return team1, team2


def create_event(db_session, event_date, event_time=time(10, 0)):
    event = Event(event_date=event_date, event_time=event_time)
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def create_match(
    db_session,
    event,
    team1,
    team2,
    status_value="A_VENIR",
    court_number=1,
):
    match = Match(
        event_id=event.id,
        team1_id=team1.id,
        team2_id=team2.id,
        court_number=court_number,
        status=status_value,
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    return match


def test_match_in_event_create_rejects_invalid_court_number():
    with pytest.raises(ValidationError) as exc_info:
        MatchInEventCreate(court_number=0, team1_id=1, team2_id=2)

    assert "piste" in str(exc_info.value)


def test_match_in_event_create_rejects_same_team():
    with pytest.raises(ValidationError) as exc_info:
        MatchInEventCreate(court_number=1, team1_id=1, team2_id=1)

    assert "quipe" in str(exc_info.value)


def test_event_create_rejects_duplicate_courts():
    matches = [
        MatchInEventCreate(court_number=1, team1_id=1, team2_id=2),
        MatchInEventCreate(court_number=1, team1_id=3, team2_id=4),
    ]

    with pytest.raises(ValidationError) as exc_info:
        EventCreate(event_date=date(2025, 1, 1), event_time=time(10, 0), matches=matches)

    assert "piste" in str(exc_info.value)


def test_event_create_rejects_duplicate_teams():
    matches = [
        MatchInEventCreate(court_number=1, team1_id=1, team2_id=2),
        MatchInEventCreate(court_number=2, team1_id=1, team2_id=3),
    ]

    with pytest.raises(ValidationError) as exc_info:
        EventCreate(event_date=date(2025, 1, 1), event_time=time(10, 0), matches=matches)

    assert "match" in str(exc_info.value)


def test_create_event_requires_admin(client, db_session, test_user):
    team1, team2 = create_two_teams(db_session)
    event_date = date.today() + timedelta(days=1)
    payload = {
        "event_date": event_date.isoformat(),
        "event_time": "10:00:00",
        "matches": [
            {"court_number": 1, "team1_id": team1.id, "team2_id": team2.id},
        ],
    }

    response = client.post(
        "/api/v1/events",
        json=payload,
        headers=auth_headers(test_user),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_event_creates_matches(client, db_session, test_admin):
    team1, team2 = create_two_teams(db_session)
    event_date = date.today() + timedelta(days=1)
    payload = {
        "event_date": event_date.isoformat(),
        "event_time": "09:00:00",
        "matches": [
            {"court_number": 1, "team1_id": team1.id, "team2_id": team2.id},
        ],
    }

    response = client.post(
        "/api/v1/events",
        json=payload,
        headers=auth_headers(test_admin),
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["event_date"] == event_date.isoformat()
    assert data["event_time"] == "09:00:00"
    assert len(data["matches"]) == 1

    match = data["matches"][0]
    assert match["court_number"] == 1
    assert match["status"] == "A_VENIR"
    assert match["team1"]["id"] == team1.id
    assert match["team2"]["id"] == team2.id


def test_get_events_filters_by_month(client, db_session, test_user):
    team1, team2 = create_two_teams(db_session)
    event_jan = create_event(db_session, date(2025, 1, 15), time(9, 0))
    event_feb = create_event(db_session, date(2025, 2, 1), time(9, 0))

    create_match(db_session, event_jan, team1, team2, court_number=1)
    create_match(db_session, event_feb, team1, team2, court_number=2)

    response = client.get(
        "/api/v1/events?month=2025-01",
        headers=auth_headers(test_user),
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == event_jan.id


def test_update_event_rejects_completed_match(client, db_session, test_admin):
    team1, team2 = create_two_teams(db_session)
    event_date = date.today() + timedelta(days=1)
    event = create_event(db_session, event_date, time(10, 0))
    create_match(db_session, event, team1, team2, status_value="TERMINE")

    response = client.put(
        f"/api/v1/events/{event.id}",
        json={"event_time": "11:00:00"},
        headers=auth_headers(test_admin),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_event_returns_404_for_missing_id(client, test_user):
    response = client.get(
        "/api/v1/events/9999",
        headers=auth_headers(test_user),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
