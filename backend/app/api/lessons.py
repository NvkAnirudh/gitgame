"""
Lessons API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.content import Lesson
from app.models.player import Player, PlayerProgress
from app.schemas.player import (
    LessonResponse,
    LessonListResponse,
    StartLessonRequest,
    CompleteLessonRequest,
    PlayerProgressResponse
)
from app.core.dependencies import get_current_player
from datetime import datetime

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/", response_model=List[LessonListResponse])
async def get_lessons(
    level: Optional[str] = Query(None, description="Filter by level: introduction, intermediate, advanced"),
    db: Session = Depends(get_db)
):
    """
    Get list of all lessons (without full content)

    Query params:
    - level: Filter by difficulty level (introduction, intermediate, advanced)
    """
    query = db.query(Lesson).order_by(Lesson.order_index)

    if level:
        query = query.filter(Lesson.level == level)

    lessons = query.all()

    # Return lessons without full content (for listing)
    return [
        LessonListResponse(
            id=lesson.id,
            title=lesson.title,
            level=lesson.level,
            order_index=lesson.order_index,
            total_sections=lesson.total_sections,
            git_commands=lesson.git_commands
        )
        for lesson in lessons
    ]


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str,
    db: Session = Depends(get_db)
):
    """
    Get full lesson content by ID
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson '{lesson_id}' not found"
        )

    return lesson


@router.post("/start", response_model=PlayerProgressResponse)
async def start_lesson(
    request: StartLessonRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Start a lesson (mark as in_progress)

    Creates or updates player progress record.
    """
    # Check if lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == request.lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson '{request.lesson_id}' not found"
        )

    # Check if progress record exists
    progress = db.query(PlayerProgress).filter(
        PlayerProgress.player_id == current_player.id,
        PlayerProgress.lesson_id == request.lesson_id
    ).first()

    if progress:
        # Update existing progress
        if progress.status == "not_started":
            progress.status = "in_progress"
            progress.started_at = datetime.utcnow()
    else:
        # Create new progress record
        progress = PlayerProgress(
            player_id=current_player.id,
            lesson_id=request.lesson_id,
            status="in_progress",
            started_at=datetime.utcnow(),
            attempts=0
        )
        db.add(progress)

    db.commit()
    db.refresh(progress)

    return progress


@router.post("/complete", response_model=PlayerProgressResponse)
async def complete_lesson(
    request: CompleteLessonRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Complete a lesson

    Updates progress record and awards XP.
    """
    # Check if progress record exists
    progress = db.query(PlayerProgress).filter(
        PlayerProgress.player_id == current_player.id,
        PlayerProgress.lesson_id == request.lesson_id
    ).first()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not started. Start the lesson first."
        )

    # Update progress
    progress.status = "completed"
    progress.completed_at = datetime.utcnow()
    progress.time_spent_seconds += request.time_spent_seconds
    progress.score = request.score
    progress.attempts += 1

    # Award XP (base 50 XP per lesson, bonus for score)
    base_xp = 50
    score_bonus = (request.score or 0) // 10  # 1 XP per 10 score points
    xp_earned = base_xp + score_bonus

    current_player.total_xp += xp_earned

    db.commit()
    db.refresh(progress)

    return progress


@router.get("/progress/me", response_model=List[PlayerProgressResponse])
async def get_my_progress(
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get current player's progress for all lessons
    """
    progress_records = db.query(PlayerProgress).filter(
        PlayerProgress.player_id == current_player.id
    ).all()

    return progress_records


@router.get("/progress/{lesson_id}", response_model=PlayerProgressResponse)
async def get_lesson_progress(
    lesson_id: str,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get current player's progress for a specific lesson
    """
    progress = db.query(PlayerProgress).filter(
        PlayerProgress.player_id == current_player.id,
        PlayerProgress.lesson_id == lesson_id
    ).first()

    if not progress:
        # Return default progress if not started
        return PlayerProgressResponse(
            id="00000000-0000-0000-0000-000000000000",
            player_id=current_player.id,
            lesson_id=lesson_id,
            status="not_started",
            started_at=None,
            completed_at=None,
            time_spent_seconds=0,
            score=None,
            attempts=0
        )

    return progress
