from pydantic import BaseModel, validator
from datetime import date, time
from typing import Optional
import re


class MatchCreate(BaseModel):
    event_date: date
    event_time: time
    court_number: int
    team1_id: int
    team2_id: int
    
    @validator('court_number')
    def validate_court(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Le numéro de piste doit être entre 1 et 10')
        return v
    
    @validator('team2_id')
    def teams_must_be_different(cls, v, values):
        if 'team1_id' in values and v == values['team1_id']:
            raise ValueError('Les deux équipes doivent être différentes')
        return v


class MatchUpdate(BaseModel):
    event_date: Optional[date] = None
    event_time: Optional[time] = None
    court_number: Optional[int] = None
    status: Optional[str] = None
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['A_VENIR', 'TERMINE', 'ANNULE']:
            raise ValueError('Statut invalide')
        return v
    
    @validator('score_team1', 'score_team2')
    def validate_score(cls, v):
        if v:
            # Format: "6-4, 6-3" ou "6-4, 3-6, 7-5"
            pattern = r'^(\d+-\d+)(,\s*\d+-\d+){1,2}$'
            if not re.match(pattern, v):
                raise ValueError('Format de score invalide (ex: "6-4, 6-3")')
        return v


class PlayerInMatch(BaseModel):
    id: int
    first_name: str
    last_name: str
    
    class Config:
        from_attributes = True


class TeamInMatch(BaseModel):
    id: int
    company: str
    player1: PlayerInMatch
    player2: PlayerInMatch
    
    class Config:
        from_attributes = True


class EventInMatch(BaseModel):
    id: int
    event_date: date
    event_time: time
    
    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    id: int
    event: EventInMatch
    court_number: int
    team1: TeamInMatch
    team2: TeamInMatch
    status: str
    score_team1: Optional[str]
    score_team2: Optional[str]
    
    class Config:
        from_attributes = True