"""
Pydantic schemas for story and narrative content
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class CharacterResponse(BaseModel):
    """Schema for character/companion data"""
    id: str
    name: str
    title: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    personality: Optional[Dict[str, Any]] = None
    specialization: Optional[str] = None

    class Config:
        from_attributes = True


class StoryArcResponse(BaseModel):
    """Schema for story arc data"""
    id: str
    name: str
    description: Optional[str] = None
    level: str
    mentor_id: Optional[str] = None
    mentor: Optional[CharacterResponse] = None
    order_index: int
    total_lessons: int
    status: Optional[str] = Field(None, description="Player's progress status for this arc")

    class Config:
        from_attributes = True


class PlayerStoryProgressResponse(BaseModel):
    """Schema for player story progress"""
    id: uuid.UUID
    player_id: uuid.UUID
    story_arc_id: str
    story_arc: Optional[StoryArcResponse] = None
    status: str  # locked, unlocked, in_progress, completed
    unlocked_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    lessons_completed: int

    class Config:
        from_attributes = True


class LessonWithStoryResponse(BaseModel):
    """Enhanced lesson response with story context"""
    id: str
    title: str
    level: str
    order_index: Optional[int] = None
    story_hook: Optional[str] = None
    content: List[Dict[str, Any]]
    learning_objectives: Optional[List[str]] = None
    practice_prompt: Optional[str] = None
    git_commands: Optional[List[str]] = None

    # Story enhancements
    mentor: Optional[CharacterResponse] = None
    story_arc: Optional[StoryArcResponse] = None
    mentor_tip: Optional[str] = Field(None, description="Contextual tip from the mentor")
    is_unlocked: bool = Field(True, description="Whether player has access to this lesson")
    prerequisites: List[str] = Field(default_factory=list, description="Required lesson IDs")

    class Config:
        from_attributes = True


class MentorTipResponse(BaseModel):
    """Mentor tip/hint for a specific context"""
    character: CharacterResponse
    tip: str
    context: str  # lesson, challenge, general


class StoryContextResponse(BaseModel):
    """Story context for current player state"""
    current_arc: Optional[StoryArcResponse] = None
    current_mentor: Optional[CharacterResponse] = None
    arcs_completed: int
    total_arcs: int
    lessons_in_current_arc: int
    lessons_completed_in_arc: int
    next_milestone: Optional[str] = None
