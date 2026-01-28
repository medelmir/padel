from datetime import date, time

from fastapi import status

from app.api.results import parse_score, determine_winner
from app.models.models import Player, Team, Event, Match


def login_get_token(client, email, password):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_player(
    db_session,
    first_name="Alex",
    last_name="Smith",
    company="Padel Corp",
    license_number="L000001",
    user_id=None,
):
    player = Player(
        first_name=first_name,
        last_name=last_name,
        company=company,
        license_number=license_number,
        user_id=user_id,
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
    score_team1,
    score_team2,
    status_value="TERMINE",
    court_number=1,
):
    match = Match(
        event_id=event.id,
        team1_id=team1.id,
        team2_id=team2.id,
        court_number=court_number,
        status=status_value,
        score_team1=score_team1,
        score_team2=score_team2,
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    return match


def test_parse_score_counts_sets_and_skips_invalid_segments():
    assert parse_score("6-4, 3-6, 7-5") == 2
    assert parse_score("6-0,6-0") == 2
    assert parse_score("invalid,6-4,6-a") == 1
    assert parse_score("") == 0


def test_determine_winner_handles_wins_and_draws():
    assert determine_winner("6-4,6-4", "4-6,4-6") == 1
    assert determine_winner("4-6,4-6", "6-4,6-4") == 2
    assert determine_winner("6-4,4-6", "4-6,6-4") == 0


def test_get_my_results_returns_ordered_results_and_stats(client, db_session, test_user):
    player = create_player(
        db_session,
        first_name="Jean",
        last_name="Doe",
        company="ACME",
        license_number="L000101",
        user_id=test_user.id,
    )
    partner = create_player(
        db_session,
        first_name="Sam",
        last_name="Partner",
        company="ACME",
        license_number="L000102",
    )
    opponent_a1 = create_player(
        db_session,
        first_name="Olivia",
        last_name="Roe",
        company="Rivals",
        license_number="L000103",
    )
    opponent_a2 = create_player(
        db_session,
        first_name="Nina",
        last_name="Rowe",
        company="Rivals",
        license_number="L000104",
    )
    opponent_b1 = create_player(
        db_session,
        first_name="Cody",
        last_name="Lane",
        company="Ninjas",
        license_number="L000105",
    )
    opponent_b2 = create_player(
        db_session,
        first_name="Mia",
        last_name="Vale",
        company="Ninjas",
        license_number="L000106",
    )

    my_team = create_team(db_session, "ACME", player, partner)
    old_opponents = create_team(db_session, "Rivals", opponent_a1, opponent_a2)
    new_opponents = create_team(db_session, "Ninjas", opponent_b1, opponent_b2)

    event_old = create_event(db_session, date(2025, 1, 1))
    event_new = create_event(db_session, date(2025, 1, 2))
    event_tie = create_event(db_session, date(2025, 1, 3))

    match_old = create_match(
        db_session,
        event_old,
        my_team,
        old_opponents,
        "6-4,6-4",
        "4-6,4-6",
        court_number=2,
    )
    match_new = create_match(
        db_session,
        event_new,
        new_opponents,
        my_team,
        "6-1,6-2",
        "1-6,2-6",
        court_number=3,
    )
    create_match(
        db_session,
        event_tie,
        my_team,
        new_opponents,
        "6-4,4-6",
        "4-6,6-4",
    )

    token = login_get_token(client, "test@example.com", "ValidP@ssw0rd123")
    response = client.get("/api/v1/results/my-results", headers=auth_headers(token))

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()

    assert payload["statistics"] == {
        "total_matches": 2,
        "wins": 1,
        "losses": 1,
        "win_rate": 50.0,
    }

    results = payload["results"]
    assert len(results) == 2

    assert results[0]["match_id"] == match_new.id
    assert results[0]["date"] == "2025-01-02"
    assert results[0]["result"] == "DEFAITE"
    assert results[0]["score"] == "1-6,2-6 vs 6-1,6-2"
    assert results[0]["opponents"]["company"] == "Ninjas"
    assert results[0]["court_number"] == 3

    assert results[1]["match_id"] == match_old.id
    assert results[1]["date"] == "2025-01-01"
    assert results[1]["result"] == "VICTOIRE"
    assert results[1]["score"] == "6-4,6-4 vs 4-6,4-6"
    assert results[1]["opponents"]["company"] == "Rivals"
    assert results[1]["court_number"] == 2


def test_get_my_results_returns_empty_when_player_has_no_teams(client, db_session, test_user):
    create_player(
        db_session,
        first_name="Solo",
        last_name="User",
        company="Lone",
        license_number="L000201",
        user_id=test_user.id,
    )

    token = login_get_token(client, "test@example.com", "ValidP@ssw0rd123")
    response = client.get("/api/v1/results/my-results", headers=auth_headers(token))

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["results"] == []
    assert payload["statistics"] == {
        "total_matches": 0,
        "wins": 0,
        "losses": 0,
        "win_rate": 0.0,
    }


def test_get_my_results_returns_404_when_player_missing(client, test_user):
    token = login_get_token(client, "test@example.com", "ValidP@ssw0rd123")
    response = client.get("/api/v1/results/my-results", headers=auth_headers(token))

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_rankings_aggregates_company_stats(client, db_session, test_user):
    alpha1 = create_player(
        db_session,
        first_name="Ana",
        last_name="Lead",
        company="Alpha",
        license_number="L000301",
    )
    alpha2 = create_player(
        db_session,
        first_name="Ben",
        last_name="Lead",
        company="Alpha",
        license_number="L000302",
    )
    bravo1 = create_player(
        db_session,
        first_name="Tess",
        last_name="Roe",
        company="Bravo",
        license_number="L000303",
    )
    bravo2 = create_player(
        db_session,
        first_name="Max",
        last_name="Roe",
        company="Bravo",
        license_number="L000304",
    )

    team_alpha = create_team(db_session, "Alpha", alpha1, alpha2)
    team_bravo = create_team(db_session, "Bravo", bravo1, bravo2)

    event_one = create_event(db_session, date(2025, 2, 1))
    event_two = create_event(db_session, date(2025, 2, 2))

    create_match(
        db_session,
        event_one,
        team_alpha,
        team_bravo,
        "6-4,6-4",
        "4-6,4-6",
        court_number=1,
    )
    create_match(
        db_session,
        event_two,
        team_alpha,
        team_bravo,
        "6-2,6-3",
        "2-6,3-6",
        court_number=1,
    )

    token = login_get_token(client, "test@example.com", "ValidP@ssw0rd123")
    response = client.get("/api/v1/results/rankings", headers=auth_headers(token))

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    rankings = payload["rankings"]

    assert len(rankings) == 2
    assert rankings[0]["position"] == 1
    assert rankings[0]["company"] == "Alpha"
    assert rankings[0]["matches_played"] == 2
    assert rankings[0]["wins"] == 2
    assert rankings[0]["losses"] == 0
    assert rankings[0]["points"] == 6
    assert rankings[0]["sets_won"] == 4
    assert rankings[0]["sets_lost"] == 0

    assert rankings[1]["position"] == 2
    assert rankings[1]["company"] == "Bravo"
    assert rankings[1]["matches_played"] == 2
    assert rankings[1]["wins"] == 0
    assert rankings[1]["losses"] == 2
    assert rankings[1]["points"] == 0
    assert rankings[1]["sets_won"] == 0
    assert rankings[1]["sets_lost"] == 4
