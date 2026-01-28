from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List

from app.database import get_db
from app.models.models import Match, Event, Team, Player, User
from app.schemas.result import MyResultsResponse, RankingsResponse, MyResultResponse, OpponentInfo, MyResultsStats, RankingEntry
from app.api.deps import get_current_user

router = APIRouter(prefix="/results", tags=["results"])


def parse_score(score_str: str) -> int:
    """Compte le nombre de sets gagnés à partir d'un score"""
    if not score_str:
        return 0
    
    sets = score_str.split(',')
    sets_won = 0
    
    for set_score in sets:
        try:
            parts = set_score.strip().split('-')
            if len(parts) == 2:
                score1 = int(parts[0])
                score2 = int(parts[1])
                if score1 > score2:
                    sets_won += 1
        except:
            continue
    
    return sets_won


def determine_winner(score_team1: str, score_team2: str) -> int:
    """Détermine le gagnant : 1 pour team1, 2 pour team2, 0 pour égalité"""
    sets_team1 = parse_score(score_team1)
    sets_team2 = parse_score(score_team2)
    
    if sets_team1 > sets_team2:
        return 1
    elif sets_team2 > sets_team1:
        return 2
    else:
        return 0


@router.get("/my-results", response_model=MyResultsResponse)
def get_my_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Résultats de l'utilisateur connecté (Joueur uniquement)"""
    
    # Trouver le joueur associé
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    
    # Trouver les équipes du joueur
    teams = db.query(Team).filter(
        or_(Team.player1_id == player.id, Team.player2_id == player.id)
    ).all()
    
    if not teams:
        return {
            "results": [],
            "statistics": {
                "total_matches": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0
            }
        }
    
    team_ids = [t.id for t in teams]
    
    # Récupérer les matchs terminés
    matches = db.query(Match).join(Event).filter(
        Match.status == "TERMINE",
        or_(Match.team1_id.in_(team_ids), Match.team2_id.in_(team_ids))
    ).order_by(Event.event_date.desc()).all()
    
    results = []
    wins = 0
    losses = 0
    
    for match in matches:
        # Déterminer si le joueur était dans team1 ou team2
        is_team1 = match.team1_id in team_ids
        my_team = match.team1 if is_team1 else match.team2
        opponent_team = match.team2 if is_team1 else match.team1
        
        # Déterminer le résultat
        winner = determine_winner(match.score_team1, match.score_team2)
        
        if winner == 0:
            continue  # Égalité, on ignore
        
        if (is_team1 and winner == 1) or (not is_team1 and winner == 2):
            result = "VICTOIRE"
            wins += 1
        else:
            result = "DEFAITE"
            losses += 1
        
        # Score formaté
        my_score = match.score_team1 if is_team1 else match.score_team2
        opponent_score = match.score_team2 if is_team1 else match.score_team1
        score_display = f"{my_score} vs {opponent_score}"
        
        results.append({
            "match_id": match.id,
            "date": match.event.event_date,
            "opponents": {
                "company": opponent_team.company,
                "players": [
                    f"{opponent_team.player1.first_name} {opponent_team.player1.last_name}",
                    f"{opponent_team.player2.first_name} {opponent_team.player2.last_name}"
                ]
            },
            "score": score_display,
            "result": result,
            "court_number": match.court_number
        })
    
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0.0
    
    return {
        "results": results,
        "statistics": {
            "total_matches": total,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 1)
        }
    }


@router.get("/rankings", response_model=RankingsResponse)
def get_rankings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Classement général des entreprises"""
    
    # Récupérer tous les matchs terminés
    matches = db.query(Match).filter(Match.status == "TERMINE").all()
    
    # Calculer les stats par entreprise
    company_stats = {}
    
    for match in matches:
        company1 = match.team1.company
        company2 = match.team2.company
        
        # Initialiser si nécessaire
        if company1 not in company_stats:
            company_stats[company1] = {
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "points": 0,
                "sets_won": 0,
                "sets_lost": 0
            }
        
        if company2 not in company_stats:
            company_stats[company2] = {
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "points": 0,
                "sets_won": 0,
                "sets_lost": 0
            }
        
        # Calculer le vainqueur
        winner = determine_winner(match.score_team1, match.score_team2)
        
        if winner == 0:
            continue  # Égalité, on ignore
        
        # Sets gagnés/perdus
        sets_team1 = parse_score(match.score_team1)
        sets_team2 = parse_score(match.score_team2)
        
        company_stats[company1]["matches_played"] += 1
        company_stats[company2]["matches_played"] += 1
        
        company_stats[company1]["sets_won"] += sets_team1
        company_stats[company1]["sets_lost"] += sets_team2
        company_stats[company2]["sets_won"] += sets_team2
        company_stats[company2]["sets_lost"] += sets_team1
        
        if winner == 1:
            company_stats[company1]["wins"] += 1
            company_stats[company1]["points"] += 3
            company_stats[company2]["losses"] += 1
        else:
            company_stats[company2]["wins"] += 1
            company_stats[company2]["points"] += 3
            company_stats[company1]["losses"] += 1
    
    # Convertir en liste et trier
    rankings = []
    for company, stats in company_stats.items():
        rankings.append({
            "company": company,
            **stats,
            "sets_diff": stats["sets_won"] - stats["sets_lost"]
        })
    
    # Tri : points DESC, victoires DESC, diff sets DESC, alphabétique
    rankings.sort(key=lambda x: (-x["points"], -x["wins"], -x["sets_diff"], x["company"]))
    
    # Ajouter les positions
    result = []
    for i, entry in enumerate(rankings, 1):
        result.append({
            "position": i,
            "company": entry["company"],
            "matches_played": entry["matches_played"],
            "wins": entry["wins"],
            "losses": entry["losses"],
            "points": entry["points"],
            "sets_won": entry["sets_won"],
            "sets_lost": entry["sets_lost"]
        })
    
    return {"rankings": result}