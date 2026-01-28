from pydantic import BaseModel, Field, validator
from typing import List
import re

class PoolBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Nom de la poule (ex: 'Poule A')")

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()  # supprime les espaces avant et après
        if not re.match(r'^[Pp]oule\s+[A-Z]$', v):
            raise ValueError("Le nom doit être au format 'Poule X' (ex: Poule A, Poule B)")
        return v


class PoolCreate(PoolBase):
    team_ids: List[int] = Field(..., min_items=6, max_items=6)

    @validator('team_ids')
    def validate_teams_length(cls, v):
        if len(v) != 6:
            raise ValueError("Une poule doit contenir exactement 6 équipes.")
        return v

class PoolUpdate(BaseModel):
    team_ids: List[int] = Field(..., min_items=6, max_items=6)

    @validator('team_ids')
    def validate_teams_length(cls, v):
        if len(v) != 6:
            raise ValueError("Une poule doit contenir exactement 6 équipes.")
        return v

class PoolResponse(PoolBase):
    id: int
    teams: List[int]

    class Config:
        from_attributes = True