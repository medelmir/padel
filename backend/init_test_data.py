#!/usr/bin/env python3
"""
Script d'initialisation des données de test pour le CI/CD
"""
from app.database import SessionLocal, init_db
from app.models.models import User, Player
from app.core.security import get_password_hash


def create_test_data():
    """Créer des données de test """
    
    print("Initialisation de la base de données...")
    init_db()
    
    db = SessionLocal()
    
    try:
        print(" Base de données initialisée")
        
        # Vérifier si des données existent déjà
        existing_user = db.query(User).first()
        if existing_user:
            print("⚠️  Des données existent déjà, nettoyage...")
            db.query(Player).delete()
            db.query(User).delete()
            db.commit()
        
        # Créer un administrateur
        print("📝 Création de l'administrateur...")
        admin_user = User(
            email="admin@padel.com",
            password_hash=get_password_hash("Admin@2025!"),
            role="ADMINISTRATEUR",
            is_active=True
        )
        db.add(admin_user)
        db.flush()
        
        admin_player = Player(
            first_name="Admin",
            last_name="Test",
            company="Test Corp",
            license_number="L000000",
            user_id=admin_user.id
        )
        db.add(admin_player)
        
        # Créer un joueur
        print("Création d'un joueur de test...")
        joueur_user = User(
            email="joueur@padel.com",
            password_hash=get_password_hash("Joueur@2025!"),
            role="JOUEUR",
            is_active=True
        )
        db.add(joueur_user)
        db.flush()
        
        joueur_player = Player(
            first_name="Jean",
            last_name="Dupont",
            company="Test Corp",
            license_number="L100001",
            user_id=joueur_user.id
        )
        db.add(joueur_player)
        
        db.commit()
        
        print("\n" + "="*50)
        print(" DONNÉES DE TEST CRÉÉES AVEC SUCCÈS !")
        print("="*50)
        print("\n COMPTES CRÉÉS :")
        print(f"   Admin : admin@padel.com / Admin@2025!")
        print(f"   Joueur: joueur@padel.com / Joueur@2025!")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"\n ERREUR : {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()