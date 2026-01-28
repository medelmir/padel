import pytest
from datetime import date
from pydantic import ValidationError

from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse


def test_player_create_accepts_valid_names_and_license():
    player = PlayerCreate(
        first_name="Jean-Paul",
        last_name="Dupont",
        company="Padel Club",
        license_number="L123456",
        email="jean.dupont@example.com",
        birth_date=date(1990, 5, 20),
    )

    assert player.first_name == "Jean-Paul"
    assert player.license_number == "L123456"
    assert player.email == "jean.dupont@example.com"
    assert player.birth_date == date(1990, 5, 20)


def test_player_create_rejects_invalid_license_format():
    with pytest.raises(ValidationError) as exc_info:
        PlayerCreate(
            first_name="Marie",
            last_name="Durand",
            company="Padel Club",
            license_number="1234567",
            email="marie.durand@example.com",
        )

    assert "license_number" in str(exc_info.value)


def test_player_create_rejects_invalid_first_name_characters():
    with pytest.raises(ValidationError) as exc_info:
        PlayerCreate(
            first_name="Marie123",
            last_name="Durand",
            company="Padel Club",
            license_number="L765432",
            email="marie.durand@example.com",
        )

    assert "lettres" in str(exc_info.value)


def test_player_update_allows_partial_payload():
    update = PlayerUpdate(photo_url="https://example.com/photo.png")

    assert update.photo_url == "https://example.com/photo.png"
    assert update.model_dump(exclude_none=True) == {"photo_url": "https://example.com/photo.png"}


def test_player_update_rejects_invalid_last_name_characters():
    with pytest.raises(ValidationError) as exc_info:
        PlayerUpdate(last_name="Durand42")

    assert "lettres" in str(exc_info.value)


def test_player_response_from_attributes():
    class PlayerRecord:
        def __init__(self):
            self.id = 1
            self.first_name = "Alice"
            self.last_name = "Martin"
            self.company = "Padel Corp"
            self.license_number = "L999999"
            self.birth_date = date(1988, 7, 14)
            self.photo_url = "https://example.com/alice.png"
            self.has_account = True

    response = PlayerResponse.model_validate(PlayerRecord())

    assert response.id == 1
    assert response.first_name == "Alice"
    assert response.license_number == "L999999"
    assert response.birth_date == date(1988, 7, 14)
    assert response.has_account is True
