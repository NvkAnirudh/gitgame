"""
Pydantic schemas for player and game data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class PlayerResponse(BaseModel):
    """Schema for player data in responses"""
    id: uuid.UUID
    user_id: uuid.UUID
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    current_level: str
    total_xp: int

    class Config:
        from_attributes = True


class PlayerProgressResponse(BaseModel):
    """Schema for player progress data"""
    id: uuid.UUID
    player_id: uuid.UUID
    lesson_id: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_spent_seconds: int
    score: Optional[int] = None
    attempts: int

    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    """Schema for lesson data in responses"""
    id: str
    title: str
    level: str
    order_index: Optional[int] = None
    story_hook: Optional[str] = None
    content: List[Dict[str, Any]]  # JSONB sections
    learning_objectives: Optional[List[str]] = None
    practice_prompt: Optional[str] = None
    git_commands: Optional[List[str]] = None
    word_count: Optional[int] = None
    total_sections: Optional[int] = None

    class Config:
        from_attributes = True


class LessonListResponse(BaseModel):
    """Schema for lesson list (without full content)"""
    id: str
    title: str
    level: str
    order_index: Optional[int] = None
    total_sections: Optional[int] = None
    git_commands: Optional[List[str]] = None

    class Config:
        from_attributes = True


class StartLessonRequest(BaseModel):
    """Schema for starting a lesson"""
    lesson_id: str


class CompleteLessonRequest(BaseModel):
    """Schema for completing a lesson"""
    lesson_id: str
    time_spent_seconds: int
    score: Optional[int] = None


class PlayerStatsResponse(BaseModel):
    """Schema for player statistics"""
    player_id: uuid.UUID
    username: str
    total_xp: int
    current_level: str
    lessons_completed: int
    lessons_in_progress: int
    challenges_completed: int
    achievements_unlocked: int
    total_learning_time_seconds: int

    class Config:
        from_attributes = True
