# FICHIER : backend/app/models/models.py
# ============================================

from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # JOUEUR ou ADMINISTRATEUR
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="JOUEUR")
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

     # Relations
    player = relationship("Player", back_populates="user", uselist=False)
    
    __table_args__ = (
        CheckConstraint("role IN ('JOUEUR', 'ADMINISTRATEUR')", name="chk_user_role"),
    )

class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    email = Column(String(255), nullable=False, index=True)
    attempts_count = Column(Integer, default=0)
    last_attempt = Column(DateTime(timezone=True))
    locked_until = Column(DateTime(timezone=True), nullable=True)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    company = Column(String(100), nullable=False)
    license_number = Column(String(7), unique=True, nullable=False, index=True)
    birth_date = Column(Date, nullable=True)
    photo_url = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="player")
    teams_as_player1 = relationship("Team", foreign_keys="Team.player1_id", back_populates="player1")
    teams_as_player2 = relationship("Team", foreign_keys="Team.player2_id", back_populates="player2")
    
    __table_args__ = (
        CheckConstraint("license_number GLOB 'L[0-9][0-9][0-9][0-9][0-9][0-9]'", name="chk_license_format"),
    )


class Pool(Base):
    __tablename__ = "pools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    teams = relationship("Team", back_populates="pool")


class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(100), nullable=False)
    player1_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player2_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    pool_id = Column(Integer, ForeignKey("pools.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    player1 = relationship("Player", foreign_keys=[player1_id], back_populates="teams_as_player1")
    player2 = relationship("Player", foreign_keys=[player2_id], back_populates="teams_as_player2")
    pool = relationship("Pool", back_populates="teams")
    matches_as_team1 = relationship("Match", foreign_keys="Match.team1_id", back_populates="team1")
    matches_as_team2 = relationship("Match", foreign_keys="Match.team2_id", back_populates="team2")
    
    __table_args__ = (
        CheckConstraint("player1_id != player2_id", name="chk_different_players"),
    )


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(Date, nullable=False, index=True)
    event_time = Column(Time, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    matches = relationship("Match", back_populates="event", cascade="all, delete-orphan")


class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    team1_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    team2_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    court_number = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="A_VENIR")
    score_team1 = Column(String(50), nullable=True)
    score_team2 = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    event = relationship("Event", back_populates="matches")
    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="matches_as_team1")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="matches_as_team2")
    
    __table_args__ = (
        CheckConstraint("court_number BETWEEN 1 AND 10", name="chk_court_number"),
        CheckConstraint("status IN ('A_VENIR', 'TERMINE', 'ANNULE')", name="chk_status"),
        CheckConstraint("team1_id != team2_id", name="chk_different_teams"),
    )
