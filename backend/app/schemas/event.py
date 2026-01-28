from pydantic import BaseModel, validator
from datetime import date, time
from typing import List, Optional
import re


class MatchInEventCreate(BaseModel):
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


class EventCreate(BaseModel):
    event_date: date
    event_time: time
    matches: List[MatchInEventCreate]
    
    @validator('matches')
    def validate_matches(cls, v):
        if len(v) < 1 or len(v) > 3:
            raise ValueError('Un événement doit contenir entre 1 et 3 matchs')
        
        # Vérifier les doublons de piste
        courts = [m.court_number for m in v]
        if len(courts) != len(set(courts)):
            raise ValueError('Deux matchs ne peuvent pas utiliser la même piste')
        
        # Vérifier qu'une équipe ne joue qu'un seul match
        teams = []
        for m in v:
            teams.extend([m.team1_id, m.team2_id])
        if len(teams) != len(set(teams)):
            raise ValueError('Une équipe ne peut jouer qu\'un seul match par événement')
        
        return v


class EventUpdate(BaseModel):
    event_date: Optional[date] = None
    event_time: Optional[time] = None


class TeamInMatch(BaseModel):
    id: int
    company: str
    
    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    id: int
    court_number: int
    team1: TeamInMatch
    team2: TeamInMatch
    status: str
    score_team1: Optional[str]
    score_team2: Optional[str]
    
    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    id: int
    event_date: date
    event_time: time
    matches: List[MatchResponse]
    
    class Config:
        from_attributes = True