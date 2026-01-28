from pydantic import BaseModel, validator
from typing import Optional


class TeamBase(BaseModel):
    player1_id: int
    player2_id: int
    pool_id: Optional[int] = None

    @validator('player2_id')
    def players_must_be_different(cls, v, values):
        if 'player1_id' in values and v == values['player1_id']:
            raise ValueError('Les deux joueurs doivent être différents')
        return v


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    player1_id: Optional[int] = None
    player2_id: Optional[int] = None
    pool_id: Optional[int] = None


class PlayerInTeam(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class PoolInTeam(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    id: int
    company: str
    player1: PlayerInTeam
    player2: PlayerInTeam
    pool: Optional[PoolInTeam]

    class Config:
        from_attributes = True
