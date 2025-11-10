"""
Story and narrative content models

These models support the story wrapper around Git learning, including
character companions and story progression tracking.
"""

from sqlalchemy import Column, String, Integer, DateTime, UUID, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Character(Base):
    """
    Character/companion profiles

    Characters are mentors that guide players through Git concepts.
    Each lesson can feature different characters to provide variety.
    """
    __tablename__ = "characters"

    id = Column(String(50), primary_key=True)  # e.g., "alex-senior-dev"
    name = Column(String(100), nullable=False)  # e.g., "Alex"
    title = Column(String(100), nullable=True)  # e.g., "Senior Developer"
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    personality = Column(JSON, nullable=True)  # e.g., {"traits": ["helpful", "patient"], "tone": "friendly"}
    specialization = Column(String(100), nullable=True)  # e.g., "Git branching expert"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    story_arcs = relationship("StoryArc", back_populates="mentor")


class StoryArc(Base):
    """
    Story arcs for lesson groupings

    Groups lessons into narrative arcs (Introduction, Intermediate, Advanced).
    Tracks overall story progression.
    """
    __tablename__ = "story_arcs"

    id = Column(String(50), primary_key=True)  # e.g., "introduction-arc"
    name = Column(String(100), nullable=False)  # e.g., "The Awakening"
    description = Column(Text, nullable=True)
    level = Column(String(20), nullable=False)  # introduction, intermediate, advanced
    mentor_id = Column(String(50), ForeignKey("characters.id"), nullable=True)
    order_index = Column(Integer, nullable=False)
    total_lessons = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    mentor = relationship("Character", back_populates="story_arcs")
    player_progress = relationship("PlayerStoryProgress", back_populates="story_arc")


class PlayerStoryProgress(Base):
    """
    Player progress through story arcs

    Tracks which story arcs a player has started and completed.
    """
    __tablename__ = "player_story_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    story_arc_id = Column(String(50), ForeignKey("story_arcs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="locked")  # locked, unlocked, in_progress, completed
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    lessons_completed = Column(Integer, default=0)

    # Relationships
    story_arc = relationship("StoryArc", back_populates="player_progress")
