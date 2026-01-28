# ============================================
# FICHIER : backend/tests/test_pool.py
# ============================================

import pytest
from pydantic import ValidationError
from app.schemas.pool import PoolBase, PoolCreate, PoolUpdate, PoolResponse

# Tests pour PoolBase

def test_poolbase_valid_name():
    """Le nom 'Poule A' est valide"""
    pool = PoolBase(name="Poule A")
    assert pool.name == "Poule A"

def test_poolbase_name_with_spaces():
    """Le nom avec espaces inutiles est accepté et nettoyé"""
    pool = PoolBase(name="  Poule B  ")
    assert pool.name == "Poule B"

def test_poolbase_invalid_name_format():
    """Nom invalide — mauvais format"""
    with pytest.raises(ValidationError):
        PoolBase(name="Pool A")  # mauvais mot
    with pytest.raises(ValidationError):
        PoolBase(name="Poule 12")  # pas une lettre majuscule
    with pytest.raises(ValidationError):
        PoolBase(name="Poule")  # pas de lettre à la fin

#  Tests pour PoolCreate

def test_poolcreate_valid_data():
    """Création d'une poule valide avec 3 équipes"""
    data = PoolCreate(name="Poule C", team_ids=[1, 2, 3])
    assert data.name == "Poule C"
    assert data.team_ids == [1, 2, 3]

def test_poolcreate_too_many_teams():
    """Erreur si plus de 6 équipes"""
    with pytest.raises(ValidationError):
        PoolCreate(name="Poule D", team_ids=[1, 2, 3, 4, 5, 6, 7])

def test_poolcreate_no_teams():
    """Erreur si aucune équipe"""
    with pytest.raises(ValidationError):
        PoolCreate(name="Poule E", team_ids=[])

#  Tests pour PoolUpdate

def test_poolupdate_valid_data():
    """Mise à jour d'une poule avec 2 équipes"""
    data = PoolUpdate(team_ids=[1, 2])
    assert data.team_ids == [1, 2]
def test_poolupdate_invalid_team_count():
    """Erreur si trop d'équipes dans la mise à jour"""
    with pytest.raises(ValidationError):
        PoolUpdate(team_ids=[1, 2, 3, 4, 5, 6, 7])

# Tests pour PoolResponse

def test_poolresponse_creation():
    """Réponse valide"""
    pool = PoolResponse(id=1, name="Poule F", teams=[10, 11])
    assert pool.id == 1
    assert pool.name == "Poule F"
    assert pool.teams == [10, 11]