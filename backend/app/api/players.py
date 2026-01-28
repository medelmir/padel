from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import Player, User, Team
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=List[PlayerResponse])
def get_players(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Liste tous les joueurs (Admin uniquement)"""
    players = db.query(Player).order_by(Player.last_name, Player.first_name).all()
    
    result = []
    for player in players:
        player_dict = {
            "id": player.id,
            "first_name": player.first_name,
            "last_name": player.last_name,
            "company": player.company,
            "license_number": player.license_number,
            "birth_date": player.birth_date,
            "photo_url": player.photo_url,
            "has_account": player.user_id is not None
        }
        result.append(player_dict)
    
    return result


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Détails d'un joueur"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    return {
        "id": player.id,
        "first_name": player.first_name,
        "last_name": player.last_name,
        "company": player.company,
        "license_number": player.license_number,
        "birth_date": player.birth_date,
        "photo_url": player.photo_url,
        "has_account": player.user_id is not None
    }


@router.post("", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_player(
    player_data: PlayerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Créer un joueur (Admin uniquement)"""
    
    # Vérifier unicité de la licence
    existing = db.query(Player).filter(Player.license_number == player_data.license_number).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ce numéro de licence existe déjà")
    
    # Créer le joueur
    new_player = Player(
        first_name=player_data.first_name,
        last_name=player_data.last_name,
        company=player_data.company,
        license_number=player_data.license_number,
        birth_date=player_data.birth_date
    )
    
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    
    return {
        "id": new_player.id,
        "first_name": new_player.first_name,
        "last_name": new_player.last_name,
        "company": new_player.company,
        "license_number": new_player.license_number,
        "birth_date": new_player.birth_date,
        "photo_url": new_player.photo_url,
        "has_account": False
    }


@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(
    player_id: int,
    player_data: PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Modifier un joueur (Admin uniquement)"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    # Mettre à jour les champs
    update_data = player_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(player, field, value)
    
    db.commit()
    db.refresh(player)
    
    return {
        "id": player.id,
        "first_name": player.first_name,
        "last_name": player.last_name,
        "company": player.company,
        "license_number": player.license_number,
        "birth_date": player.birth_date,
        "photo_url": player.photo_url,
        "has_account": player.user_id is not None
    }


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Supprimer un joueur (Admin uniquement)"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    # Vérifier qu'il n'est dans aucune équipe
    in_team = db.query(Team).filter(
        (Team.player1_id == player_id) | (Team.player2_id == player_id)
    ).first()
    
    if in_team:
        raise HTTPException(
            status_code=400, 
            detail="Impossible de supprimer un joueur qui est dans une équipe"
        )
    
    db.delete(player)
    db.commit()
    
    return None