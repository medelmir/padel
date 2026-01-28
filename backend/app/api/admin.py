from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
import string

from app.database import get_db
from app.models.models import User, Player
from app.schemas.admin import (
    CreateAccountRequest,
    CreateAccountResponse,
    ResetPasswordResponse,
    UserWithPlayer
)
from app.api.deps import require_admin
from app.core.security import get_password_hash

router = APIRouter(prefix="/admin", tags=["admin"])


def generate_temporary_password(length: int = 16) -> str:
    """Génère un mot de passe temporaire sécurisé"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))

# S'assurer qu'il contient au moins une majuscule, minuscule, chiffre et spécial
    if not any(c.isupper() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_uppercase)
    if not any(c.islower() for c in password):
        password = password[:-2] + secrets.choice(string.ascii_lowercase) + password[-1]
    if not any(c.isdigit() for c in password):
        password = password[:-3] + secrets.choice(string.digits) + password[-2:]
    if not any(c in "!@#$%^&*" for c in password):
        password = password[:-4] + secrets.choice("!@#$%^&*") + password[-3:]

    return password


@router.get("/accounts", response_model=List[UserWithPlayer])
def get_all_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Liste tous les comptes utilisateurs (Admin uniquement)"""
    users = db.query(User).all()

    result = []
    for user in users:
        player = db.query(Player).filter(Player.user_id == user.id).first()

        result.append({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "player_id": player.id if player else None,
            "player_name": f"{player.first_name} {player.last_name}" if player else None,
            "company": player.company if player else None
        })

    return result


@router.get("/players-without-account")
def get_players_without_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Liste des joueurs sans compte (Admin uniquement)"""
    players = db.query(Player).filter(Player.user_id == None).all()

    return [
        {
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "company": p.company,
            "license_number": p.license_number
        }
        for p in players
    ]


@router.post("/accounts/create", response_model=CreateAccountResponse, status_code=status.HTTP_201_CREATED)
def create_account_for_player(
    account_data: CreateAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Créer un compte pour un joueur (Admin uniquement)"""

# Vérifier que le joueur existe
    player = db.query(Player).filter(Player.id == account_data.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")

# Vérifier que le joueur n'a pas déjà un compte
    if player.user_id:
        raise HTTPException(status_code=400, detail="Ce joueur a déjà un compte")

# Générer un email si le joueur n'en a pas (utiliser licence@padel.com)
    email = f"{player.license_number.lower()}@padel.com"

# Vérifier que l'email n'existe pas déjà
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Un compte avec cet email existe déjà")

# Générer un mot de passe temporaire
    temp_password = generate_temporary_password()

# Créer le compte
    new_user = User(
        email=email,
        password_hash=get_password_hash(temp_password),
        role=account_data.role,
        is_active=True,
        must_change_password=True
    )

    db.add(new_user)
    db.flush()

# Lier le joueur au compte
    player.user_id = new_user.id

    db.commit()

    return {
        "message": "Compte créé avec succès",
        "email": email,
        "temporary_password": temp_password,
        "warning": "Ce mot de passe ne sera affiché qu'une seule fois. Notez-le précieusement."
    }


@router.post("/accounts/{user_id}/reset-password", response_model=ResetPasswordResponse)
def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Réinitialiser le mot de passe d'un utilisateur (Admin uniquement)"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

# Générer un nouveau mot de passe temporaire
    temp_password = generate_temporary_password()

# Mettre à jour le mot de passe
    user.password_hash = get_password_hash(temp_password)
    user.must_change_password = True

    db.commit()

    return {
        "message": "Mot de passe réinitialisé avec succès",
        "temporary_password": temp_password,
        "warning": "Ce mot de passe ne sera affiché qu'une seule fois. Communiquez-le à l'utilisateur."
    }


@router.put("/accounts/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Activer/Désactiver un compte utilisateur (Admin uniquement)"""

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas désactiver votre propre compte")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    user.is_active = not user.is_active
    db.commit()

    status_text = "activé" if user.is_active else "désactivé"
    return {"message": f"Compte {status_text} avec succès"}


@router.delete("/accounts/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Supprimer un compte utilisateur (Admin uniquement)"""

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

# Délier le joueur si lié
    player = db.query(Player).filter(Player.user_id == user_id).first()
    if player:
        player.user_id = None

    db.delete(user)
    db.commit()

    return None