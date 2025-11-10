"""
Story & Narrative API endpoints

Provides story context, character companions, and progression tracking
to enhance Git learning with engaging narratives.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.story import Character, StoryArc, PlayerStoryProgress
from app.models.player import Player, PlayerProgress
from app.models.content import Lesson
from app.schemas.story import (
    CharacterResponse,
    StoryArcResponse,
    PlayerStoryProgressResponse,
    MentorTipResponse,
    StoryContextResponse
)
from app.core.dependencies import get_current_player

router = APIRouter(prefix="/story", tags=["story"])


@router.get("/characters", response_model=List[CharacterResponse])
async def get_characters(
    db: Session = Depends(get_db)
):
    """
    Get all character/companion profiles

    Returns list of mentors and companions in the Git Quest universe.
    """
    characters = db.query(Character).all()
    return characters


@router.get("/characters/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific character profile
    """
    character = db.query(Character).filter(Character.id == character_id).first()

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )

    return character


@router.get("/arcs", response_model=List[StoryArcResponse])
async def get_story_arcs(
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get all story arcs with player progress

    Returns story arcs ordered by progression, with status for current player.
    """
    arcs = db.query(StoryArc).order_by(StoryArc.order_index).all()

    # Get player progress for each arc
    progress_records = db.query(PlayerStoryProgress).filter(
        PlayerStoryProgress.player_id == current_player.id
    ).all()
    progress_map = {p.story_arc_id: p for p in progress_records}

    result = []
    for arc in arcs:
        # Load mentor if exists
        mentor = arc.mentor

        # Get player progress status
        progress = progress_map.get(arc.id)
        status = progress.status if progress else "locked"

        result.append(StoryArcResponse(
            id=arc.id,
            name=arc.name,
            description=arc.description,
            level=arc.level,
            mentor_id=arc.mentor_id,
            mentor=CharacterResponse(
                id=mentor.id,
                name=mentor.name,
                title=mentor.title,
                avatar_url=mentor.avatar_url,
                bio=mentor.bio,
                personality=mentor.personality,
                specialization=mentor.specialization
            ) if mentor else None,
            order_index=arc.order_index,
            total_lessons=arc.total_lessons,
            status=status
        ))

    return result


@router.get("/arcs/{arc_id}", response_model=StoryArcResponse)
async def get_story_arc(
    arc_id: str,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get a specific story arc with player progress
    """
    arc = db.query(StoryArc).filter(StoryArc.id == arc_id).first()

    if not arc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story arc '{arc_id}' not found"
        )

    # Get player progress
    progress = db.query(PlayerStoryProgress).filter(
        PlayerStoryProgress.player_id == current_player.id,
        PlayerStoryProgress.story_arc_id == arc_id
    ).first()

    status = progress.status if progress else "locked"
    mentor = arc.mentor

    return StoryArcResponse(
        id=arc.id,
        name=arc.name,
        description=arc.description,
        level=arc.level,
        mentor_id=arc.mentor_id,
        mentor=CharacterResponse(
            id=mentor.id,
            name=mentor.name,
            title=mentor.title,
            avatar_url=mentor.avatar_url,
            bio=mentor.bio,
            personality=mentor.personality,
            specialization=mentor.specialization
        ) if mentor else None,
        order_index=arc.order_index,
        total_lessons=arc.total_lessons,
        status=status
    )


@router.get("/progress", response_model=List[PlayerStoryProgressResponse])
async def get_my_story_progress(
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get current player's story progression

    Returns progress for all story arcs.
    """
    progress_records = db.query(PlayerStoryProgress).filter(
        PlayerStoryProgress.player_id == current_player.id
    ).all()

    result = []
    for progress in progress_records:
        arc = progress.story_arc
        mentor = arc.mentor if arc else None

        result.append(PlayerStoryProgressResponse(
            id=progress.id,
            player_id=progress.player_id,
            story_arc_id=progress.story_arc_id,
            story_arc=StoryArcResponse(
                id=arc.id,
                name=arc.name,
                description=arc.description,
                level=arc.level,
                mentor_id=arc.mentor_id,
                mentor=CharacterResponse(
                    id=mentor.id,
                    name=mentor.name,
                    title=mentor.title,
                    avatar_url=mentor.avatar_url,
                    bio=mentor.bio,
                    personality=mentor.personality,
                    specialization=mentor.specialization
                ) if mentor else None,
                order_index=arc.order_index,
                total_lessons=arc.total_lessons
            ) if arc else None,
            status=progress.status,
            unlocked_at=progress.unlocked_at,
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            lessons_completed=progress.lessons_completed
        ))

    return result


@router.get("/context", response_model=StoryContextResponse)
async def get_story_context(
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get current story context for player

    Returns current arc, mentor, and progression milestones.
    """
    # Get player's current level
    current_level = current_player.current_level

    # Find current arc
    current_arc = db.query(StoryArc).filter(
        StoryArc.level == current_level
    ).first()

    # Count completed lessons in current arc
    if current_arc:
        completed_count = db.query(func.count(PlayerProgress.id)).filter(
            PlayerProgress.player_id == current_player.id,
            PlayerProgress.status == 'completed'
        ).join(Lesson).filter(
            Lesson.level == current_arc.level
        ).scalar()
    else:
        completed_count = 0

    # Count total arcs completed
    arcs_completed = db.query(func.count(PlayerStoryProgress.id)).filter(
        PlayerStoryProgress.player_id == current_player.id,
        PlayerStoryProgress.status == 'completed'
    ).scalar()

    total_arcs = db.query(func.count(StoryArc.id)).scalar()

    # Determine next milestone
    next_milestone = None
    if current_arc and completed_count < current_arc.total_lessons:
        remaining = current_arc.total_lessons - completed_count
        next_milestone = f"Complete {remaining} more lesson{'s' if remaining != 1 else ''} to finish {current_arc.name}"

    return StoryContextResponse(
        current_arc=StoryArcResponse(
            id=current_arc.id,
            name=current_arc.name,
            description=current_arc.description,
            level=current_arc.level,
            mentor_id=current_arc.mentor_id,
            mentor=CharacterResponse(
                id=current_arc.mentor.id,
                name=current_arc.mentor.name,
                title=current_arc.mentor.title,
                avatar_url=current_arc.mentor.avatar_url,
                bio=current_arc.mentor.bio,
                personality=current_arc.mentor.personality,
                specialization=current_arc.mentor.specialization
            ) if current_arc.mentor else None,
            order_index=current_arc.order_index,
            total_lessons=current_arc.total_lessons
        ) if current_arc else None,
        current_mentor=CharacterResponse(
            id=current_arc.mentor.id,
            name=current_arc.mentor.name,
            title=current_arc.mentor.title,
            avatar_url=current_arc.mentor.avatar_url,
            bio=current_arc.mentor.bio,
            personality=current_arc.mentor.personality,
            specialization=current_arc.mentor.specialization
        ) if current_arc and current_arc.mentor else None,
        arcs_completed=arcs_completed,
        total_arcs=total_arcs,
        lessons_in_current_arc=current_arc.total_lessons if current_arc else 0,
        lessons_completed_in_arc=completed_count,
        next_milestone=next_milestone
    )


@router.get("/mentor/tip/{lesson_id}", response_model=MentorTipResponse)
async def get_mentor_tip(
    lesson_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a mentor tip for a specific lesson

    Returns contextual guidance from the mentor assigned to this lesson's arc.
    """
    # Find lesson
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson '{lesson_id}' not found"
        )

    # Find story arc for this lesson
    arc = db.query(StoryArc).filter(StoryArc.level == lesson.level).first()

    if not arc or not arc.mentor:
        # Default mentor if none assigned
        tip = f"Focus on understanding the '{lesson.title}' concept. Practice makes perfect!"
        character = CharacterResponse(
            id="default",
            name="Git Quest Guide",
            title="Learning Assistant",
            avatar_url=None,
            bio="Your guide through Git mastery",
            personality=None,
            specialization="Git fundamentals"
        )
    else:
        mentor = arc.mentor
        # Generate contextual tip based on lesson objectives
        objectives = lesson.learning_objectives or []
        if objectives:
            tip = f"Master {objectives[0].lower()} to progress. Remember: Git is about understanding the flow, not memorizing commands."
        else:
            tip = f"Take your time with '{lesson.title}'. Understanding this concept is crucial for your Git journey."

        character = CharacterResponse(
            id=mentor.id,
            name=mentor.name,
            title=mentor.title,
            avatar_url=mentor.avatar_url,
            bio=mentor.bio,
            personality=mentor.personality,
            specialization=mentor.specialization
        )

    return MentorTipResponse(
        character=character,
        tip=tip,
        context="lesson"
    )
