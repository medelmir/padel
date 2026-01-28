from pydantic import BaseModel, EmailStr, validator
from datetime import date
from typing import Optional
import re


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if v and not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]{2,50}$', v):
            raise ValueError('Nom invalide (2-50 caractères, lettres uniquement)')
        return v
    
    @validator('birth_date')
    def validate_age(cls, v):
        if v:
            from datetime import date as dt_date
            today = dt_date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 16:
                raise ValueError('Vous devez avoir au moins 16 ans')
            if v > today:
                raise ValueError('La date de naissance ne peut pas être dans le futur')
        return v


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 12:
            raise ValueError('Le mot de passe doit contenir au moins 12 caractères')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not re.search(r'\d', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Le mot de passe doit contenir au moins un caractère spécial')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v


class UserInfo(BaseModel):
    id: int
    email: str
    role: str
    
    class Config:
        from_attributes = True


class PlayerInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    company: str
    license_number: str
    birth_date: Optional[date]
    photo_url: Optional[str]
    
    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    user: UserInfo
    player: Optional[PlayerInfo]
