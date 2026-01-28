import io
import os
from fastapi import status

from app.models.models import Player, User
from app.core.security import get_password_hash


def create_player_for_user(db_session, user):
	player = Player(
		first_name="Jean",
		last_name="Dupont",
		company="ACME Corp",
		license_number="L123456",
		user_id=user.id
	)
	db_session.add(player)
	db_session.commit()
	db_session.refresh(player)
	return player


def login_get_token(client, email, password):
	resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
	assert resp.status_code == status.HTTP_200_OK
	return resp.json()["access_token"]


def test_get_my_profile(client, db_session, test_user):
	# Préparer un player lié à l'utilisateur
	create_player_for_user(db_session, test_user)

	token = login_get_token(client, "test@example.com", "ValidP@ssw0rd123")
	headers = {"Authorization": f"Bearer {token}"}

	resp = client.get("/api/v1/profile/me", headers=headers)
	assert resp.status_code == status.HTTP_200_OK
	data = resp.json()
	assert data["user"]["email"] == "test@example.com"
	assert data["player"]["first_name"] == "Jean"


def test_update_my_profile(client, db_session, test_user):
	create_player_for_user(db_session, test_user)

	token = login_get_token(client, "test@example.com", "ValidP@ssw0rd123")
	headers = {"Authorization": f"Bearer {token}"}

	payload = {
		"first_name": "Pierre",
		"last_name": "Martin",
		"email": "updated@example.com",
	}

	resp = client.put("/api/v1/profile/me", json=payload, headers=headers)
	assert resp.status_code == status.HTTP_200_OK

	# Vérifier que les changements sont persistés
	resp2 = client.get("/api/v1/profile/me", headers=headers)
	data = resp2.json()
	assert data["player"]["first_name"] == "Pierre"
	assert data["user"]["email"] == "updated@example.com"


def test_upload_and_delete_photo(client, db_session, test_user, tmp_path):
	# create player
	player = create_player_for_user(db_session, test_user)

	token = login_get_token(client, "test@example.com", "ValidP@ssw0rd123")
	headers = {"Authorization": f"Bearer {token}"}

	# prepare a fake png file content
	png_bytes = b"\x89PNG\r\n\x1a\n" + b"0" * 64

	files = {"file": ("avatar.png", io.BytesIO(png_bytes), "image/png")}

	resp = client.post("/api/v1/profile/me/photo", headers=headers, files=files)
	assert resp.status_code == status.HTTP_200_OK
	data = resp.json()
	assert "photo_url" in data

	# now delete
	resp_del = client.delete("/api/v1/profile/me/photo", headers=headers)
	assert resp_del.status_code == status.HTTP_204_NO_CONTENT


def test_change_password(client, db_session):
	# create user with known password
	user = User(
		email="pwduser@example.com",
		password_hash=get_password_hash("OldP@ssw0rd123"),
		role="JOUEUR",
		is_active=True
	)
	db_session.add(user)
	db_session.commit()
	db_session.refresh(user)

	token = login_get_token(client, "pwduser@example.com", "OldP@ssw0rd123")
	headers = {"Authorization": f"Bearer {token}"}

	payload = {
		"current_password": "OldP@ssw0rd123",
		"new_password": "NewValidP@ssw0rd1!",
		"confirm_password": "NewValidP@ssw0rd1!"
	}

	resp = client.post("/api/v1/profile/me/change-password", json=payload, headers=headers)
	assert resp.status_code == status.HTTP_200_OK

	# Can login with new password
	resp_login = client.post("/api/v1/auth/login", json={"email": "pwduser@example.com", "password": "NewValidP@ssw0rd1!"})
	assert resp_login.status_code == status.HTTP_200_OK

