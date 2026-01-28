from datetime import date, time, timedelta

import pytest
from fastapi import status
from pydantic import ValidationError

from app.core.security import create_access_token
from app.models.models import Player, Team, Event, Match
from app.schemas.match import MatchCreate, MatchUpdate


def auth_headers(user):
    token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role}
    )
    return {"Authorization": f"Bearer {token}"}


def create_player(db_session, first_name, last_name, company, license_number):
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
    player1 = create_player(db_session, "Alex", "Stone", "Alpha", "L200001")
    player2 = create_player(db_session, "Blake", "Stone", "Alpha", "L200002")
    player3 = create_player(db_session, "Casey", "Vale", "Bravo", "L200003")
    player4 = create_player(db_session, "Dana", "Vale", "Bravo", "L200004")
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


def test_match_create_rejects_invalid_court_number():
    with pytest.raises(ValidationError) as exc_info:
        MatchCreate(
            event_date=date(2025, 1, 1),
            event_time=time(10, 0),
            court_number=0,
            team1_id=1,
            team2_id=2,
        )

    assert "piste" in str(exc_info.value)


def test_match_create_rejects_same_team():
    with pytest.raises(ValidationError) as exc_info:
        MatchCreate(
            event_date=date(2025, 1, 1),
            event_time=time(10, 0),
            court_number=1,
            team1_id=1,
            team2_id=1,
        )

    assert "quipe" in str(exc_info.value)


def test_match_update_rejects_invalid_status():
    with pytest.raises(ValidationError) as exc_info:
        MatchUpdate(status="INVALID")

    assert "Statut" in str(exc_info.value)


def test_match_update_rejects_invalid_score_format():
    with pytest.raises(ValidationError) as exc_info:
        MatchUpdate(score_team1="6-4-3")

    assert "score" in str(exc_info.value)


def test_create_match_requires_admin(client, db_session, test_user):
    team1, team2 = create_two_teams(db_session)
    payload = {
        "event_date": (date.today() + timedelta(days=1)).isoformat(),
        "event_time": "10:00:00",
        "court_number": 1,
        "team1_id": team1.id,
        "team2_id": team2.id,
    }

    response = client.post(
        "/api/v1/matches",
        json=payload,
        headers=auth_headers(test_user),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_match_creates_event_when_missing(client, db_session, test_admin):
    team1, team2 = create_two_teams(db_session)
    event_date = date.today() + timedelta(days=2)
    payload = {
        "event_date": event_date.isoformat(),
        "event_time": "09:30:00",
        "court_number": 2,
        "team1_id": team1.id,
        "team2_id": team2.id,
    }

    response = client.post(
        "/api/v1/matches",
        json=payload,
        headers=auth_headers(test_admin),
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["event"]["event_date"] == event_date.isoformat()
    assert data["event"]["event_time"] == "09:30:00"
    assert data["court_number"] == 2
    assert data["status"] == "A_VENIR"


def test_create_match_rejects_duplicate_court_in_event(client, db_session, test_admin):
    team1, team2 = create_two_teams(db_session)
    event_date = date.today() + timedelta(days=3)
    event_time = time(10, 0)
    event = create_event(db_session, event_date, event_time)
    create_match(db_session, event, team1, team2, court_number=1)

    extra_team1 = create_team(
        db_session,
        "Charlie",
        create_player(db_session, "Eli", "Stone", "Charlie", "L200005"),
        create_player(db_session, "Finn", "Stone", "Charlie", "L200006"),
    )
    extra_team2 = create_team(
        db_session,
        "Delta",
        create_player(db_session, "Gale", "Vale", "Delta", "L200007"),
        create_player(db_session, "Hana", "Vale", "Delta", "L200008"),
    )

    payload = {
        "event_date": event_date.isoformat(),
        "event_time": event_time.isoformat(),
        "court_number": 1,
        "team1_id": extra_team1.id,
        "team2_id": extra_team2.id,
    }

    response = client.post(
        "/api/v1/matches",
        json=payload,
        headers=auth_headers(test_admin),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_matches_filters_upcoming(client, db_session, test_user):
    team1, team2 = create_two_teams(db_session)
    event_soon = create_event(db_session, date.today() + timedelta(days=5), time(9, 0))
    event_late = create_event(db_session, date.today() + timedelta(days=40), time(9, 0))
    match_soon = create_match(db_session, event_soon, team1, team2, court_number=1)
    create_match(db_session, event_late, team1, team2, court_number=2)

    response = client.get(
        "/api/v1/matches?upcoming=true",
        headers=auth_headers(test_user),
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    ids = [item["id"] for item in data]
    assert match_soon.id in ids
    assert len(data) == 1


def test_get_matches_my_matches_filters_to_player_team(client, db_session, test_user):
    player = create_player(db_session, "Jean", "Doe", "ACME", "L200010")
    player.user_id = test_user.id
    db_session.commit()

    partner = create_player(db_session, "Sam", "Partner", "ACME", "L200011")
    opponent1 = create_player(db_session, "Olivia", "Roe", "Rivals", "L200012")
    opponent2 = create_player(db_session, "Nina", "Roe", "Rivals", "L200013")

    my_team = create_team(db_session, "ACME", player, partner)
    other_team = create_team(db_session, "Rivals", opponent1, opponent2)

    event = create_event(db_session, date.today() + timedelta(days=1), time(11, 0))
    match_my = create_match(db_session, event, my_team, other_team, court_number=1)

    extra_team1, extra_team2 = create_two_teams(db_session)
    create_match(db_session, event, extra_team1, extra_team2, court_number=2)

    response = client.get(
        "/api/v1/matches?my_matches=true",
        headers=auth_headers(test_user),
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert [item["id"] for item in data] == [match_my.id]


def test_update_match_rejects_date_change_when_not_upcoming(client, db_session, test_admin):
    team1, team2 = create_two_teams(db_session)
    event = create_event(db_session, date.today() + timedelta(days=1), time(10, 0))
    match = create_match(db_session, event, team1, team2, status_value="TERMINE")

    response = client.put(
        f"/api/v1/matches/{match.id}",
        json={"event_date": (date.today() + timedelta(days=2)).isoformat()},
        headers=auth_headers(test_admin),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_match_rejects_non_upcoming(client, db_session, test_admin):
    team1, team2 = create_two_teams(db_session)
    event = create_event(db_session, date.today() + timedelta(days=1), time(10, 0))
    match = create_match(db_session, event, team1, team2, status_value="TERMINE")

    response = client.delete(
        f"/api/v1/matches/{match.id}",
        headers=auth_headers(test_admin),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_match_returns_404_for_missing_id(client, test_user):
    response = client.get(
        "/api/v1/matches/9999",
        headers=auth_headers(test_user),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
