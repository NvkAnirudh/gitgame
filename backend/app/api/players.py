"""
Players API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.player import Player, PlayerProgress, ChallengeAttempt, PlayerAchievement
from app.schemas.player import PlayerResponse, PlayerStatsResponse
from app.core.dependencies import get_current_player

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/me", response_model=PlayerResponse)
async def get_my_profile(current_player: Player = Depends(get_current_player)):
    """
    Get current player profile
    """
    return current_player


@router.get("/me/stats", response_model=PlayerStatsResponse)
async def get_my_stats(
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get current player statistics
    """
    # Count lessons completed
    lessons_completed = db.query(func.count(PlayerProgress.id)).filter(
        PlayerProgress.player_id == current_player.id,
        PlayerProgress.status == "completed"
    ).scalar() or 0

    # Count lessons in progress
    lessons_in_progress = db.query(func.count(PlayerProgress.id)).filter(
        PlayerProgress.player_id == current_player.id,
        PlayerProgress.status == "in_progress"
    ).scalar() or 0

    # Count challenges completed
    challenges_completed = db.query(func.count(ChallengeAttempt.id.distinct())).filter(
        ChallengeAttempt.player_id == current_player.id,
        ChallengeAttempt.success == True
    ).scalar() or 0

    # Count achievements
    achievements_unlocked = db.query(func.count(PlayerAchievement.achievement_id)).filter(
        PlayerAchievement.player_id == current_player.id
    ).scalar() or 0

    # Total learning time
    total_learning_time = db.query(func.sum(PlayerProgress.time_spent_seconds)).filter(
        PlayerProgress.player_id == current_player.id
    ).scalar() or 0

    return PlayerStatsResponse(
        player_id=current_player.id,
        username=current_player.username,
        total_xp=current_player.total_xp,
        current_level=current_player.current_level,
        lessons_completed=lessons_completed,
        lessons_in_progress=lessons_in_progress,
        challenges_completed=challenges_completed,
        achievements_unlocked=achievements_unlocked,
        total_learning_time_seconds=total_learning_time
    )
