# Backend - Corpo Padel

Backend FastAPI avec authentification JWT et protection anti-brute force.

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

## Initialisation de la base de données

```bash
python -c "from app.database import init_db; init_db()"
```

## Lancement

```bash
uvicorn app.main:app --reload --port 8000
```

API : http://localhost:8000
Documentation : http://localhost:8000/docs

## Tests

```bash
pytest
pytest --cov=app --cov-report=html
```

## Structure

- `app/api/` : Routes API
- `app/core/` : Configuration et sécurité
- `app/models/` : Modèles SQLAlchemy
- `app/schemas/` : Schémas Pydantic
- `tests/` : Tests unitaires
