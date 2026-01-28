from pydantic import BaseModel
from datetime import date
from typing import List


class OpponentInfo(BaseModel):
    company: str
    players: List[str]


class MyResultResponse(BaseModel):
    match_id: int
    date: date
    opponents: OpponentInfo
    score: str
    result: str  # VICTOIRE ou DEFAITE
    court_number: int


class MyResultsStats(BaseModel):
    total_matches: int
    wins: int
    losses: int
    win_rate: float


class MyResultsResponse(BaseModel):
    results: List[MyResultResponse]
    statistics: MyResultsStats


class RankingEntry(BaseModel):
    position: int
    company: str
    matches_played: int
    wins: int
    losses: int
    points: int
    sets_won: int
    sets_lost: int


class RankingsResponse(BaseModel):
    rankings: List[RankingEntry]