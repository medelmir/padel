from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.models import Match, Event, Team, Player, User
from app.schemas.match import MatchCreate, MatchUpdate, MatchResponse
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=List[MatchResponse])
def get_matches(
    upcoming: Optional[bool] = None,
    team_id: Optional[int] = None,
    status: Optional[str] = None,
    my_matches: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des matchs avec filtres"""
    query = db.query(Match).join(Event)
    
    # Filtre : 30 prochains jours
    if upcoming:
        today = date.today()
        in_30_days = today + timedelta(days=30)
        query = query.filter(
            Event.event_date >= today,
            Event.event_date <= in_30_days
        )
    
    # Filtre : équipe spécifique
    if team_id:
        query = query.filter(
            or_(Match.team1_id == team_id, Match.team2_id == team_id)
        )
    
    # Filtre : statut
    if status:
        query = query.filter(Match.status == status)
    
    # Filtre : mes matchs (pour les joueurs)
    if my_matches and current_user.role == "JOUEUR":
        # Trouver le joueur associé
        player = db.query(Player).filter(Player.user_id == current_user.id).first()
        if player:
            # Trouver les équipes du joueur
            teams = db.query(Team).filter(
                or_(Team.player1_id == player.id, Team.player2_id == player.id)
            ).all()
            team_ids = [t.id for t in teams]
            
            if team_ids:
                query = query.filter(
                    or_(Match.team1_id.in_(team_ids), Match.team2_id.in_(team_ids))
                )
            else:
                # Aucune équipe, retourner vide
                return []
    
    matches = query.order_by(Event.event_date, Event.event_time).all()
    return matches


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Détails d'un match"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    return match


@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(
    match_data: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Créer un match (Admin uniquement)"""
    
    # Vérifier la date
    if match_data.event_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="La date du match doit être >= aujourd'hui"
        )
    
    # Vérifier que les équipes existent
    team1 = db.query(Team).filter(Team.id == match_data.team1_id).first()
    team2 = db.query(Team).filter(Team.id == match_data.team2_id).first()
    
    if not team1 or not team2:
        raise HTTPException(status_code=404, detail="Une ou plusieurs équipes non trouvées")
    
    # Créer ou trouver l'événement
    event = db.query(Event).filter(
        Event.event_date == match_data.event_date,
        Event.event_time == match_data.event_time
    ).first()
    
    if not event:
        event = Event(
            event_date=match_data.event_date,
            event_time=match_data.event_time
        )
        db.add(event)
        db.flush()
    
    # Vérifier qu'il n'y a pas déjà 3 matchs pour cet événement
    matches_count = db.query(Match).filter(Match.event_id == event.id).count()
    if matches_count >= 3:
        raise HTTPException(
            status_code=400,
            detail="Un événement ne peut pas avoir plus de 3 matchs"
        )
    
    # Vérifier que la piste n'est pas déjà prise pour cet événement
    court_taken = db.query(Match).filter(
        Match.event_id == event.id,
        Match.court_number == match_data.court_number
    ).first()
    
    if court_taken:
        raise HTTPException(
            status_code=400,
            detail="Cette piste est déjà occupée pour cet événement"
        )
    
    # Vérifier qu'aucune équipe ne joue déjà dans cet événement
    team_playing = db.query(Match).filter(
        Match.event_id == event.id,
        or_(
            Match.team1_id.in_([match_data.team1_id, match_data.team2_id]),
            Match.team2_id.in_([match_data.team1_id, match_data.team2_id])
        )
    ).first()
    
    if team_playing:
        raise HTTPException(
            status_code=400,
            detail="Une des équipes joue déjà dans cet événement"
        )
    
    # Créer le match
    new_match = Match(
        event_id=event.id,
        court_number=match_data.court_number,
        team1_id=match_data.team1_id,
        team2_id=match_data.team2_id,
        status="A_VENIR"
    )
    
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    
    return new_match


@router.put("/{match_id}", response_model=MatchResponse)
def update_match(
    match_id: int,
    match_data: MatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Modifier un match (Admin uniquement)"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    update_data = match_data.dict(exclude_unset=True)
    
    # Si on modifie la date/heure et que le statut n'est pas A_VENIR
    if ('event_date' in update_data or 'event_time' in update_data) and match.status != "A_VENIR":
        raise HTTPException(
            status_code=400,
            detail="Impossible de modifier la date/heure d'un match non à venir"
        )
    
    # Si on modifie la date/heure, créer ou trouver le bon événement
    if 'event_date' in update_data or 'event_time' in update_data:
        new_date = update_data.get('event_date', match.event.event_date)
        new_time = update_data.get('event_time', match.event.event_time)
        
        new_event = db.query(Event).filter(
            Event.event_date == new_date,
            Event.event_time == new_time
        ).first()
        
        if not new_event:
            new_event = Event(event_date=new_date, event_time=new_time)
            db.add(new_event)
            db.flush()
        
        match.event_id = new_event.id
        update_data.pop('event_date', None)
        update_data.pop('event_time', None)
    
    # Mettre à jour les autres champs
    for field, value in update_data.items():
        setattr(match, field, value)
    
    db.commit()
    db.refresh(match)
    
    return match


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Supprimer un match (Admin uniquement)"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    # Vérifier que le statut est A_VENIR
    if match.status != "A_VENIR":
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer un match qui n'est pas à venir"
        )
    
    db.delete(match)
    db.commit()
    
    return None