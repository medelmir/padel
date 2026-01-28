from pydantic import BaseModel
from typing import Optional


class CreateAccountRequest(BaseModel):
    player_id: int
    role: str = "JOUEUR"


class CreateAccountResponse(BaseModel):
    message: str
    email: str
    temporary_password: str
    warning: str


class ResetPasswordResponse(BaseModel):
    message: str
    temporary_password: str
    warning: str


class UserWithPlayer(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    player_id: Optional[int]
    player_name: Optional[str]
    company: Optional[str]

    class Config:
        from_attributes = True