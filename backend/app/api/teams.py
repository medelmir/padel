from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import Team, Player, User, Match, Pool
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=List[TeamResponse])
def get_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return db.query(Team).all()


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")
    return team


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if team_data.player1_id == team_data.player2_id:
        raise HTTPException(status_code=400, detail="Les deux joueurs doivent être différents")

    player1 = db.query(Player).filter(Player.id == team_data.player1_id).first()
    player2 = db.query(Player).filter(Player.id == team_data.player2_id).first()

    if not player1 or not player2:
        raise HTTPException(status_code=404, detail="Un ou deux joueurs non trouvés")

    if player1.company != player2.company:
        raise HTTPException(status_code=400, detail="Les joueurs doivent appartenir à la même entreprise")

    for player_id in [team_data.player1_id, team_data.player2_id]:
        existing_team = db.query(Team).filter(
            (Team.player1_id == player_id) | (Team.player2_id == player_id)
        ).first()
        if existing_team:
            raise HTTPException(status_code=409, detail=f"Le joueur {player_id} est déjà dans une autre équipe")

    if team_data.pool_id:
        pool = db.query(Pool).filter(Pool.id == team_data.pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail='Poule non trouvee')
        pool_size = db.query(Team).filter(Team.pool_id == team_data.pool_id).count()
        if pool_size >= 6:
            raise HTTPException(status_code=400, detail='Cette poule est deja complete (6 equipes maximum)')

    new_team = Team(
        company=player1.company,
        player1_id=team_data.player1_id,
        player2_id=team_data.player2_id,
        pool_id=team_data.pool_id
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")

    match_played = db.query(Match).filter(
        (Match.team1_id == team_id) | (Match.team2_id == team_id)
    ).first()
    if match_played:
        raise HTTPException(status_code=400, detail="Impossible de modifier une équipe ayant joué un match")

    update_data = team_data.dict(exclude_unset=True)

    if "pool_id" in update_data:
        new_pool_id = update_data["pool_id"]
        if new_pool_id is not None:
            pool = db.query(Pool).filter(Pool.id == new_pool_id).first()
            if not pool:
                raise HTTPException(status_code=404, detail="Poule non trouvé")
            pool_size = db.query(Team).filter(Team.pool_id == new_pool_id).count()
            if new_pool_id != team.pool_id and pool_size >= 6:
                raise HTTPException(status_code=400, detail="Cette poule est deja complète (6 équipes maximum)")

    for field, value in update_data.items():
        setattr(team, field, value)

    db.commit()
    db.refresh(team)
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")

    match_played = db.query(Match).filter(
        (Match.team1_id == team_id) | (Match.team2_id == team_id)
    ).first()
    if match_played:
        raise HTTPException(status_code=400, detail="Impossible de supprimer une équipe ayant joué un match")

    db.delete(team)
    db.commit()
