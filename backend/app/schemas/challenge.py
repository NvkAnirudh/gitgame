"""
Pydantic schemas for challenges and challenge attempts
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class ChallengeResponse(BaseModel):
    """Schema for full challenge data in responses"""
    id: str
    lesson_id: str
    title: str
    type: str  # crisis, command_mastery, quiz, speed_run, boss
    difficulty: Optional[int] = None
    scenario: str
    success_criteria: Dict[str, Any]
    hints: Optional[List[str]] = None
    git_state: Optional[Dict[str, Any]] = None
    time_limit_seconds: Optional[int] = None
    max_score: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChallengeListResponse(BaseModel):
    """Schema for challenge list (without full details)"""
    id: str
    lesson_id: str
    title: str
    type: str
    difficulty: Optional[int] = None
    max_score: int
    time_limit_seconds: Optional[int] = None

    class Config:
        from_attributes = True


class StartChallengeRequest(BaseModel):
    """Schema for starting a challenge attempt"""
    challenge_id: str


class SubmitChallengeRequest(BaseModel):
    """Schema for submitting a challenge solution"""
    commands_used: List[str] = Field(..., description="List of Git commands executed")
    time_taken_seconds: int = Field(..., ge=0, description="Time taken in seconds")
    hints_used: int = Field(default=0, ge=0, description="Number of hints used")
    final_state: Optional[Dict[str, Any]] = Field(None, description="Final Git repository state")


class ChallengeAttemptResponse(BaseModel):
    """Schema for challenge attempt results"""
    id: uuid.UUID
    player_id: uuid.UUID
    challenge_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    success: bool
    commands_used: Optional[List[str]] = None
    score: int
    time_taken_seconds: Optional[int] = None
    hints_used: int
    feedback: Optional[str] = Field(None, description="Feedback message about the attempt")

    class Config:
        from_attributes = True


class ChallengeValidationResult(BaseModel):
    """Schema for challenge validation results"""
    success: bool
    score: int
    feedback: str
    criteria_met: List[str] = Field(default_factory=list, description="Success criteria that were met")
    criteria_failed: List[str] = Field(default_factory=list, description="Success criteria that failed")


class ChallengeLeaderboardEntry(BaseModel):
    """Schema for leaderboard entry"""
    player_username: str
    score: int
    time_taken_seconds: int
    completed_at: datetime
    rank: int

    class Config:
        from_attributes = True


class ChallengeStatsResponse(BaseModel):
    """Schema for challenge statistics"""
    challenge_id: str
    total_attempts: int
    successful_attempts: int
    success_rate: float
    average_score: float
    average_time_seconds: float
    fastest_time_seconds: Optional[int] = None
