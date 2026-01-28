from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Pool, Team
from app.schemas.pool import PoolCreate, PoolUpdate, PoolResponse

router = APIRouter(prefix="/pools", tags=["Pools"])


# GET : Liste de toutes les poules
@router.get("/", response_model=list[PoolResponse])
def get_pools(db: Session = Depends(get_db)):
    pools = db.query(Pool).all()
    result = []
    for pool in pools:
        team_ids = [team.id for team in db.query(Team).filter(Team.pool_id == pool.id).all()]
        result.append(PoolResponse(id=pool.id, name=pool.name, teams=team_ids))
    return result


# POST : Créer une nouvelle poule
@router.post("/", response_model=PoolResponse)
def create_pool(pool_data: PoolCreate, db: Session = Depends(get_db)):
    # Vérifie si le nom existe déjà
    if db.query(Pool).filter(Pool.name == pool_data.name).first():
        raise HTTPException(status_code=400, detail="Une poule avec ce nom existe déjà.")

    # Vérifie que toutes les équipes existent
    teams = db.query(Team).filter(Team.id.in_(pool_data.team_ids)).all()
    if len(teams) != 6:
        raise HTTPException(status_code=400, detail="Certaines équipes n'existent pas.")
    if len(teams) != len(pool_data.team_ids):
        raise HTTPException(
            status_code=400,
            detail=f"Certaines équipes n'existent pas ou leur nombre est incorrect ({len(pool_data.team_ids)} attendu)."
        )


    # Crée la poule
    new_pool = Pool(name=pool_data.name)
    db.add(new_pool)
    db.commit()
    db.refresh(new_pool)

    # Associe les équipes à la poule
    for team in teams:
        team.pool_id = new_pool.id
    db.commit()

    return PoolResponse(id=new_pool.id, name=new_pool.name, teams=pool_data.team_ids)

@router.delete("/{pool_id}", status_code=204)
def delete_pool(pool_id: int, db: Session = Depends(get_db)):
    pool = db.query(Pool).filter(Pool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    # Supprime d'abord les équipes associées pour éviter les contraintes
    db.query(Team).filter(Team.pool_id == pool.id).update({"pool_id": None})
    db.commit()

    db.delete(pool)
    db.commit()


    for team in teams:
        team.pool_id = new_pool.id
    db.commit()

    return PoolResponse(id=new_pool.id, name=new_pool.name, teams=pool_data.team_ids)