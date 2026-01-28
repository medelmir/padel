from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from app.database import get_db
from app.models.models import User, Player
from app.schemas.profile import ProfileResponse, ProfileUpdate, PasswordChange
from app.api.deps import get_current_user
from app.core.security import verify_password, get_password_hash

router = APIRouter(prefix="/profile", tags=["profile"])

# Configuration upload
UPLOAD_DIR = Path("uploads/profiles")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer le profil de l'utilisateur connecté"""
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    
    return {
        "user": current_user,
        "player": player
    }


@router.put("/me", response_model=ProfileResponse)
def update_my_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Modifier le profil de l'utilisateur connecté"""
    
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Profil joueur non trouvé")
    
    update_data = profile_data.dict(exclude_unset=True)
    
    # Mise à jour de l'email dans User
    if 'email' in update_data:
        # Vérifier unicité
        existing = db.query(User).filter(
            User.email == update_data['email'],
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")
        
        current_user.email = update_data['email']
        update_data.pop('email')
    
    # Mise à jour des autres champs dans Player
    for field, value in update_data.items():
        setattr(player, field, value)
    
    db.commit()
    db.refresh(current_user)
    db.refresh(player)
    
    return {
        "user": current_user,
        "player": player
    }


@router.post("/me/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload une photo de profil"""
    
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Profil joueur non trouvé")
    
    # Vérifier l'extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Format de fichier non autorisé. Utilisez JPG, JPEG ou PNG"
        )
    
    # Lire le fichier pour vérifier la taille
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Fichier trop volumineux. Maximum 2MB"
        )
    
    # Supprimer l'ancienne photo si elle existe
    if player.photo_url:
        old_photo_path = Path(player.photo_url)
        if old_photo_path.exists():
            old_photo_path.unlink()
    
    # Sauvegarder le nouveau fichier
    filename = f"player_{player.id}{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Mettre à jour la base de données
    player.photo_url = str(file_path)
    db.commit()
    
    return {
        "message": "Photo uploadée avec succès",
        "photo_url": str(file_path)
    }


@router.delete("/me/photo", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile_photo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer la photo de profil"""
    
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Profil joueur non trouvé")
    
    if not player.photo_url:
        raise HTTPException(status_code=404, detail="Aucune photo à supprimer")
    
    # Supprimer le fichier
    photo_path = Path(player.photo_url)
    if photo_path.exists():
        photo_path.unlink()
    
    # Mettre à jour la base de données
    player.photo_url = None
    db.commit()
    
    return None


@router.post("/me/change-password")
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Changer le mot de passe"""
    
    # Vérifier le mot de passe actuel
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Mot de passe actuel incorrect"
        )
    
    # Vérifier que le nouveau mot de passe est différent
    if verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Le nouveau mot de passe doit être différent de l'ancien"
        )
    
    # Mettre à jour le mot de passe
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.must_change_password = False
    db.commit()
    
    return {"message": "Mot de passe modifié avec succès"}
