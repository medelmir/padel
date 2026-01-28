from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import json

from app.database import get_db
from app.models.models import Event, Match, Team, User
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/events", tags=["events"])
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

@router.get("", response_model=List[EventResponse])
def get_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    month: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste tous les événements avec filtres optionnels"""
    query = db.query(Event)
    
    if start_date:
        query = query.filter(Event.event_date >= start_date)
    
    if end_date:
        query = query.filter(Event.event_date <= end_date)
    
    if month:  # Format: YYYY-MM
        try:
            year, month_num = month.split('-')
            query = query.filter(
                Event.event_date >= date(int(year), int(month_num), 1)
            )
            # Dernier jour du mois
            if int(month_num) == 12:
                next_month = date(int(year) + 1, 1, 1)
            else:
                next_month = date(int(year), int(month_num) + 1, 1)
            query = query.filter(Event.event_date < next_month)
        except:
            pass
    
    events = query.order_by(Event.event_date, Event.event_time).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Détails d'un événement"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    return event


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Créer un événement avec ses matchs (Admin uniquement)"""
    
    # Vérifier que la date est >= aujourd'hui
    from datetime import date as dt_date
    if event_data.event_date < dt_date.today():
        raise HTTPException(
            status_code=400,
            detail="La date de l'événement doit être >= aujourd'hui"
        )
    
    # Vérifier que les équipes existent
    all_team_ids = []
    for match in event_data.matches:
        all_team_ids.extend([match.team1_id, match.team2_id])
    
    teams = db.query(Team).filter(Team.id.in_(all_team_ids)).all()
    if len(teams) != len(set(all_team_ids)):
        raise HTTPException(status_code=404, detail="Une ou plusieurs équipes non trouvées")
    
    # Créer l'événement
    new_event = Event(
        event_date=event_data.event_date,
        event_time=event_data.event_time
    )
    db.add(new_event)
    db.flush()  # Pour obtenir l'ID
    
    # Créer les matchs
    for match_data in event_data.matches:
        new_match = Match(
            event_id=new_event.id,
            court_number=match_data.court_number,
            team1_id=match_data.team1_id,
            team2_id=match_data.team2_id,
            status="A_VENIR"
        )
        db.add(new_match)
    
    db.commit()
    db.refresh(new_event)
    
    return new_event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Modifier un événement (Admin uniquement)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    # Vérifier qu'aucun match n'est terminé
    match_termine = db.query(Match).filter(
        Match.event_id == event_id,
        Match.status == "TERMINE"
    ).first()
    
    if match_termine:
        raise HTTPException(
            status_code=400,
            detail="Impossible de modifier un événement avec des matchs terminés"
        )
    
    # Mettre à jour
    update_data = event_data.dict(exclude_unset=True)
    
    # Vérifier la date si modifiée
    if 'event_date' in update_data:
        from datetime import date as dt_date
        if update_data['event_date'] < dt_date.today():
            raise HTTPException(
                status_code=400,
                detail="La date de l'événement doit être >= aujourd'hui"
            )
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Supprimer un événement (Admin uniquement)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    # Vérifier qu'aucun match n'est terminé
    match_termine = db.query(Match).filter(
        Match.event_id == event_id,
        Match.status == "TERMINE"
    ).first()
    
    if match_termine:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer un événement avec des matchs terminés"
        )
    
    db.delete(event)
    db.commit()
    
    return None