"""
Game Sessions API endpoints

Tracks player gaming sessions for analytics and engagement metrics
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.player import Player, GameSession
from app.schemas.player import (
    GameSessionResponse,
    StartSessionRequest,
    EndSessionRequest,
    SessionStatsResponse
)
from app.core.dependencies import get_current_player

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=GameSessionResponse)
async def start_session(
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Start a new game session

    Creates a new session record for the current player.
    Automatically ends any existing active sessions.
    """
    # End any existing active sessions for this player
    active_sessions = db.query(GameSession).filter(
        GameSession.player_id == current_player.id,
        GameSession.ended_at.is_(None)
    ).all()

    for session in active_sessions:
        # Calculate duration
        duration = int((datetime.utcnow() - session.started_at).total_seconds())
        session.ended_at = datetime.utcnow()
        session.duration_seconds = duration

    # Create new session
    new_session = GameSession(
        player_id=current_player.id,
        started_at=datetime.utcnow(),
        lessons_completed=0,
        challenges_completed=0,
        xp_earned=0
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return GameSessionResponse(
        id=new_session.id,
        player_id=new_session.player_id,
        started_at=new_session.started_at,
        ended_at=new_session.ended_at,
        duration_seconds=new_session.duration_seconds,
        lessons_completed=new_session.lessons_completed,
        challenges_completed=new_session.challenges_completed,
        xp_earned=new_session.xp_earned,
        is_active=True
    )


@router.post("/end", response_model=GameSessionResponse)
async def end_session(
    request: EndSessionRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    End a game session

    Marks the session as ended and calculates duration.
    """
    # Find session
    session = db.query(GameSession).filter(
        GameSession.id == request.session_id,
        GameSession.player_id == current_player.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.ended_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already ended"
        )

    # End session
    session.ended_at = datetime.utcnow()
    session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())

    db.commit()
    db.refresh(session)

    return GameSessionResponse(
        id=session.id,
        player_id=session.player_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_seconds=session.duration_seconds,
        lessons_completed=session.lessons_completed,
        challenges_completed=session.challenges_completed,
        xp_earned=session.xp_earned,
        is_active=False
    )


@router.get("/current", response_model=Optional[GameSessionResponse])
async def get_current_session(
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get the current active session for the player

    Returns None if no active session exists.
    """
    session = db.query(GameSession).filter(
        GameSession.player_id == current_player.id,
        GameSession.ended_at.is_(None)
    ).order_by(GameSession.started_at.desc()).first()

    if not session:
        return None

    return GameSessionResponse(
        id=session.id,
        player_id=session.player_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_seconds=session.duration_seconds,
        lessons_completed=session.lessons_completed,
        challenges_completed=session.challenges_completed,
        xp_earned=session.xp_earned,
        is_active=True
    )


@router.get("/history", response_model=List[GameSessionResponse])
async def get_session_history(
    limit: int = Query(20, ge=1, le=100, description="Number of sessions to return"),
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get player's session history

    Returns recent sessions ordered by start time (most recent first).
    """
    sessions = db.query(GameSession).filter(
        GameSession.player_id == current_player.id
    ).order_by(GameSession.started_at.desc()).limit(limit).all()

    return [
        GameSessionResponse(
            id=session.id,
            player_id=session.player_id,
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration_seconds=session.duration_seconds,
            lessons_completed=session.lessons_completed,
            challenges_completed=session.challenges_completed,
            xp_earned=session.xp_earned,
            is_active=(session.ended_at is None)
        )
        for session in sessions
    ]


@router.get("/{session_id}", response_model=GameSessionResponse)
async def get_session(
    session_id: str,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get a specific session by ID
    """
    session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.player_id == current_player.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return GameSessionResponse(
        id=session.id,
        player_id=session.player_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_seconds=session.duration_seconds,
        lessons_completed=session.lessons_completed,
        challenges_completed=session.challenges_completed,
        xp_earned=session.xp_earned,
        is_active=(session.ended_at is None)
    )


@router.get("/stats/me", response_model=SessionStatsResponse)
async def get_my_session_stats(
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get session statistics for current player

    Returns aggregated stats across all sessions.
    """
    sessions = db.query(GameSession).filter(
        GameSession.player_id == current_player.id
    ).all()

    total_sessions = len(sessions)

    # Calculate stats
    completed_sessions = [s for s in sessions if s.ended_at is not None]
    total_playtime = sum(s.duration_seconds or 0 for s in completed_sessions)
    avg_duration = total_playtime / len(completed_sessions) if completed_sessions else 0.0

    total_xp = sum(s.xp_earned for s in sessions)
    total_lessons = sum(s.lessons_completed for s in sessions)
    total_challenges = sum(s.challenges_completed for s in sessions)

    longest_session = max((s.duration_seconds for s in completed_sessions if s.duration_seconds), default=0)

    # Calculate streak (consecutive days with sessions)
    current_streak = calculate_session_streak(sessions)

    return SessionStatsResponse(
        total_sessions=total_sessions,
        total_playtime_seconds=total_playtime,
        average_session_duration_seconds=avg_duration,
        total_xp_earned=total_xp,
        total_lessons_completed=total_lessons,
        total_challenges_completed=total_challenges,
        longest_session_seconds=longest_session,
        current_streak_days=current_streak
    )


@router.post("/{session_id}/increment-lesson", response_model=GameSessionResponse)
async def increment_lesson_count(
    session_id: str,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Increment lesson completion count for a session

    Used internally when a lesson is completed.
    """
    session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.player_id == current_player.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session.lessons_completed += 1
    db.commit()
    db.refresh(session)

    return GameSessionResponse(
        id=session.id,
        player_id=session.player_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_seconds=session.duration_seconds,
        lessons_completed=session.lessons_completed,
        challenges_completed=session.challenges_completed,
        xp_earned=session.xp_earned,
        is_active=(session.ended_at is None)
    )


@router.post("/{session_id}/increment-challenge", response_model=GameSessionResponse)
async def increment_challenge_count(
    session_id: str,
    xp_earned: int = Query(0, description="XP earned from challenge"),
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Increment challenge completion count and XP for a session

    Used internally when a challenge is completed.
    """
    session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.player_id == current_player.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session.challenges_completed += 1
    session.xp_earned += xp_earned
    db.commit()
    db.refresh(session)

    return GameSessionResponse(
        id=session.id,
        player_id=session.player_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_seconds=session.duration_seconds,
        lessons_completed=session.lessons_completed,
        challenges_completed=session.challenges_completed,
        xp_earned=session.xp_earned,
        is_active=(session.ended_at is None)
    )


# Helper functions

def calculate_session_streak(sessions: List[GameSession]) -> int:
    """
    Calculate the current streak of consecutive days with sessions

    Args:
        sessions: List of player sessions

    Returns:
        Number of consecutive days with at least one session
    """
    if not sessions:
        return 0

    # Get unique dates with sessions
    session_dates = set()
    for session in sessions:
        date = session.started_at.date()
        session_dates.add(date)

    # Sort dates descending
    sorted_dates = sorted(session_dates, reverse=True)

    # Count consecutive days from today
    streak = 0
    expected_date = datetime.utcnow().date()

    for date in sorted_dates:
        if date == expected_date:
            streak += 1
            expected_date = expected_date - timedelta(days=1)
        elif date < expected_date:
            # Gap in streak
            break

    return streak
