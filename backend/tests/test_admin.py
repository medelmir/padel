# ============================================
# FICHIER : backend/tests/test_admin.py
# ============================================

from fastapi import status

from app.api.admin import generate_temporary_password
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.models import Player, User


def auth_headers(user: User) -> dict:
    """Return Authorization header for the given user."""
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })
    return {"Authorization": f"Bearer {token}"}


def create_player(db_session, first_name="Alice", last_name="Doe", company="Padel Corp", license_number="L000001", user_id=None):
    player = Player(
        first_name=first_name,
        last_name=last_name,
        company=company,
        license_number=license_number,
        user_id=user_id
    )
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)
    return player


def test_generate_temporary_password_contains_required_characters():
    password = generate_temporary_password()

    assert len(password) == 16
    assert any(c.isupper() for c in password)
    assert any(c.islower() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(c in "!@#$%^&*" for c in password)


def test_get_all_accounts_returns_linked_player_data(client, db_session, test_admin):
    user = User(
        email="player1@example.com",
        password_hash=get_password_hash("UserPass123!"),
        role="JOUEUR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    player = create_player(
        db_session,
        first_name="Sam",
        last_name="Stone",
        company="ACME",
        license_number="L111111",
        user_id=user.id
    )

    response = client.get("/api/v1/admin/accounts", headers=auth_headers(test_admin))

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    account = next((item for item in data if item["id"] == user.id), None)
    assert account is not None
    assert account["player_id"] == player.id
    assert account["player_name"] == f"{player.first_name} {player.last_name}"
    assert account["company"] == player.company


def test_get_players_without_account_lists_only_unlinked_players(client, db_session, test_admin):
    unattached = create_player(
        db_session,
        first_name="Unlinked",
        last_name="Player",
        company="Solo Corp",
        license_number="L222222"
    )

    linked_user = User(
        email="linked@example.com",
        password_hash=get_password_hash("LinkedPass123!"),
        role="JOUEUR",
        is_active=True
    )
    db_session.add(linked_user)
    db_session.commit()
    db_session.refresh(linked_user)

    linked_player = create_player(
        db_session,
        first_name="Linked",
        last_name="User",
        company="Duo Corp",
        license_number="L333333",
        user_id=linked_user.id
    )

    response = client.get("/api/v1/admin/players-without-account", headers=auth_headers(test_admin))

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    ids = [player["id"] for player in body]
    assert unattached.id in ids
    assert linked_player.id not in ids


def test_create_account_for_player_creates_user_and_links_player(client, db_session, test_admin):
    player = create_player(
        db_session,
        first_name="Alice",
        last_name="Woods",
        company="Forest Corp",
        license_number="L444444"
    )

    response = client.post(
        "/api/v1/admin/accounts/create",
        json={"player_id": player.id, "role": "JOUEUR"},
        headers=auth_headers(test_admin)
    )

    assert response.status_code == status.HTTP_201_CREATED
    payload = response.json()
    expected_email = f"{player.license_number.lower()}@padel.com"
    assert payload["email"] == expected_email
    assert "temporary_password" in payload

    user = db_session.query(User).filter(User.email == expected_email).first()
    assert user is not None
    db_session.refresh(player)
    assert player.user_id == user.id
    assert user.role == "JOUEUR"
    assert user.must_change_password is True
    assert verify_password(payload["temporary_password"], user.password_hash)


def test_reset_user_password_sets_temporary_password(client, db_session, test_admin):
    user = User(
        email="reset@example.com",
        password_hash=get_password_hash("OldPass123!"),
        role="JOUEUR",
        is_active=True,
        must_change_password=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    old_hash = user.password_hash

    response = client.post(
        f"/api/v1/admin/accounts/{user.id}/reset-password",
        headers=auth_headers(test_admin)
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    db_session.refresh(user)
    assert user.must_change_password is True
    assert user.password_hash != old_hash
    assert verify_password(data["temporary_password"], user.password_hash)


def test_toggle_user_active_flips_status(client, db_session, test_admin):
    user = User(
        email="toggle@example.com",
        password_hash=get_password_hash("TogglePass123!"),
        role="JOUEUR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.put(
        f"/api/v1/admin/accounts/{user.id}/toggle-active",
        headers=auth_headers(test_admin)
    )

    assert response.status_code == status.HTTP_200_OK
    db_session.refresh(user)
    assert user.is_active is False


def test_delete_user_account_removes_user_and_unlinks_player(client, db_session, test_admin):
    user = User(
        email="delete@example.com",
        password_hash=get_password_hash("DeletePass123!"),
        role="JOUEUR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    player = create_player(
        db_session,
        first_name="Dana",
        last_name="Miles",
        company="Delete Corp",
        license_number="L555555",
        user_id=user.id
    )

    response = client.delete(
        f"/api/v1/admin/accounts/{user.id}",
        headers=auth_headers(test_admin)
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db_session.query(User).filter(User.id == user.id).first() is None

    db_session.refresh(player)
    assert player.user_id is None
