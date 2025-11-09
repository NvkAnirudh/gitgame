"""
Player and game progress models
"""

from sqlalchemy import Column, String, Integer, DateTime, UUID, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Player(Base):
    """Player game profile"""
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    current_level = Column(String(20), default="introduction")
    total_xp = Column(Integer, default=0, index=True)

    # Relationships
    user = relationship("User", back_populates="player")
    progress = relationship("PlayerProgress", back_populates="player", cascade="all, delete-orphan")
    challenge_attempts = relationship("ChallengeAttempt", back_populates="player", cascade="all, delete-orphan")
    achievements = relationship("PlayerAchievement", back_populates="player", cascade="all, delete-orphan")
    events = relationship("PlayerEvent", back_populates="player", cascade="all, delete-orphan")
    sessions = relationship("GameSession", back_populates="player", cascade="all, delete-orphan")


class PlayerProgress(Base):
    """Player lesson completion progress"""
    __tablename__ = "player_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id = Column(String(50), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="not_started", index=True)  # not_started, in_progress, completed
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    score = Column(Integer, nullable=True)
    attempts = Column(Integer, default=0)

    # Relationships
    player = relationship("Player", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress_records")


class ChallengeAttempt(Base):
    """Player challenge attempts"""
    __tablename__ = "challenge_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(String(50), ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    success = Column(Boolean, default=False, index=True)
    commands_used = Column(JSON, nullable=True)
    score = Column(Integer, default=0)
    time_taken_seconds = Column(Integer, nullable=True)
    hints_used = Column(Integer, default=0)

    # Relationships
    player = relationship("Player", back_populates="challenge_attempts")
    challenge = relationship("Challenge", back_populates="attempts")


class PlayerAchievement(Base):
    """Player unlocked achievements"""
    __tablename__ = "player_achievements"

    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), primary_key=True)
    achievement_id = Column(String(50), ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    player = relationship("Player", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="players")


class PlayerEvent(Base):
    """Player events for analytics"""
    __tablename__ = "player_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    player = relationship("Player", back_populates="events")


class GameSession(Base):
    """Game sessions for tracking playtime"""
    __tablename__ = "game_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    lessons_completed = Column(Integer, default=0)
    challenges_completed = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)

    # Relationships
    player = relationship("Player", back_populates="sessions")
