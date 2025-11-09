"""
Content models (lessons, challenges, achievements, git commands)
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Lesson(Base):
    """Tutorial lesson content"""
    __tablename__ = "lessons"

    id = Column(String(50), primary_key=True)
    filename = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    level = Column(String(20), nullable=False, index=True)  # introduction, intermediate, advanced
    order_index = Column(Integer, index=True)
    story_hook = Column(Text, nullable=True)
    content = Column(JSON, nullable=False)  # JSONB - tutorial sections
    learning_objectives = Column(JSON, nullable=True)
    practice_prompt = Column(Text, nullable=True)
    git_commands = Column(JSON, nullable=True)
    word_count = Column(Integer, nullable=True)
    total_sections = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    challenges = relationship("Challenge", back_populates="lesson", cascade="all, delete-orphan")
    progress_records = relationship("PlayerProgress", back_populates="lesson")


class GitCommand(Base):
    """Git command reference"""
    __tablename__ = "git_commands"

    id = Column(String(50), primary_key=True)
    command = Column(String(100), unique=True, nullable=False)
    syntax = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), index=True, nullable=True)
    difficulty = Column(Integer, index=True, nullable=True)  # 1-5
    examples = Column(JSON, nullable=True)
    common_mistakes = Column(JSON, nullable=True)
    related_commands = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Challenge(Base):
    """Challenge scenarios"""
    __tablename__ = "challenges"

    id = Column(String(50), primary_key=True)
    lesson_id = Column(String(50), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, index=True)  # crisis, command_mastery, quiz, speed_run, boss
    difficulty = Column(Integer, index=True, nullable=True)  # 1-5
    scenario = Column(Text, nullable=False)
    success_criteria = Column(JSON, nullable=False)
    hints = Column(JSON, nullable=True)
    git_state = Column(JSON, nullable=True)
    time_limit_seconds = Column(Integer, nullable=True)
    max_score = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lesson = relationship("Lesson", back_populates="challenges")
    attempts = relationship("ChallengeAttempt", back_populates="challenge")


class Achievement(Base):
    """Achievement definitions"""
    __tablename__ = "achievements"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    badge_icon = Column(String(255), nullable=True)
    category = Column(String(50), index=True, nullable=True)
    unlock_criteria = Column(JSON, nullable=False)
    points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    players = relationship("PlayerAchievement", back_populates="achievement")
