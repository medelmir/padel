from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date
from typing import Optional
import re


class PlayerBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    company: str = Field(..., min_length=2, max_length=100)
    license_number: str = Field(..., pattern=r'^L\d{6}$')
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', v):
            raise ValueError('Seuls les lettres, espaces, tirets et apostrophes sont autorisés')
        return v


class PlayerCreate(PlayerBase):
    email: EmailStr
    birth_date: Optional[date] = None


    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v:
            today = date.today()
            if v > today:
                raise ValueError('La date de naissance ne peut pas etre dans le futur')
        return v


class PlayerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    birth_date: Optional[date] = None
    photo_url: Optional[str] = None
    company: Optional[str] = Field(None, min_length=2, max_length=100)
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if v and not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', v):
            raise ValueError('Seuls les lettres, espaces, tirets et apostrophes sont autorisés')
        return v


    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v:
            today = date.today()
            if v > today:
                raise ValueError('La date de naissance ne peut pas etre dans le futur')
        return v


class PlayerResponse(PlayerBase):
    id: int
    birth_date: Optional[date]
    photo_url: Optional[str]
    has_account: bool
    
    class Config:
        from_attributes = True
