"""
Challenges API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.content import Challenge
from app.models.player import Player, ChallengeAttempt
from app.schemas.challenge import (
    ChallengeResponse,
    ChallengeListResponse,
    StartChallengeRequest,
    SubmitChallengeRequest,
    ChallengeAttemptResponse,
    ChallengeValidationResult,
    ChallengeLeaderboardEntry,
    ChallengeStatsResponse
)
from app.core.dependencies import get_current_player
from app.services.git_sandbox import get_sandbox_manager, GitSandbox, GitSandboxError
from datetime import datetime

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.get("/", response_model=List[ChallengeListResponse])
async def get_challenges(
    lesson_id: Optional[str] = Query(None, description="Filter by lesson ID"),
    type: Optional[str] = Query(None, description="Filter by type: crisis, command_mastery, quiz, speed_run, boss"),
    db: Session = Depends(get_db)
):
    """
    Get list of all challenges

    Query params:
    - lesson_id: Filter challenges by lesson
    - type: Filter by challenge type
    """
    query = db.query(Challenge)

    if lesson_id:
        query = query.filter(Challenge.lesson_id == lesson_id)

    if type:
        query = query.filter(Challenge.type == type)

    challenges = query.all()

    return [
        ChallengeListResponse(
            id=challenge.id,
            lesson_id=challenge.lesson_id,
            title=challenge.title,
            type=challenge.type,
            difficulty=challenge.difficulty,
            max_score=challenge.max_score,
            time_limit_seconds=challenge.time_limit_seconds
        )
        for challenge in challenges
    ]


@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: str,
    db: Session = Depends(get_db)
):
    """
    Get full challenge details by ID

    Returns the complete challenge including scenario, success criteria, and git_state
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge '{challenge_id}' not found"
        )

    return challenge


@router.post("/start", response_model=ChallengeAttemptResponse)
async def start_challenge(
    request: StartChallengeRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Start a challenge attempt

    Creates a new challenge attempt record and initializes the git sandbox
    """
    # Check if challenge exists
    challenge = db.query(Challenge).filter(Challenge.id == request.challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge '{request.challenge_id}' not found"
        )

    # Initialize Git sandbox with challenge state
    sandbox_manager = get_sandbox_manager()
    try:
        sandbox = sandbox_manager.create_sandbox(git_state=challenge.git_state)
        sandbox_id = sandbox.sandbox_id
    except GitSandboxError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sandbox: {str(e)}"
        )

    # Create new attempt record
    # Store sandbox_id in commands_used for now (as metadata)
    attempt = ChallengeAttempt(
        player_id=current_player.id,
        challenge_id=request.challenge_id,
        started_at=datetime.utcnow(),
        success=False,
        score=0,
        hints_used=0,
        commands_used={'_sandbox_id': sandbox_id}  # Store sandbox ID
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return ChallengeAttemptResponse(
        id=attempt.id,
        player_id=attempt.player_id,
        challenge_id=attempt.challenge_id,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        success=attempt.success,
        commands_used=None,  # Don't expose sandbox_id to client
        score=attempt.score,
        time_taken_seconds=attempt.time_taken_seconds,
        hints_used=attempt.hints_used,
        feedback=f"Challenge started! Sandbox initialized. Good luck, Guardian!"
    )


@router.post("/{challenge_id}/submit", response_model=ChallengeAttemptResponse)
async def submit_challenge(
    challenge_id: str,
    request: SubmitChallengeRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Submit a challenge solution

    Validates the solution against success criteria and records the result
    """
    # Check if challenge exists
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge '{challenge_id}' not found"
        )

    # Find the most recent uncompleted attempt
    attempt = db.query(ChallengeAttempt).filter(
        ChallengeAttempt.player_id == current_player.id,
        ChallengeAttempt.challenge_id == challenge_id,
        ChallengeAttempt.completed_at.is_(None)
    ).order_by(ChallengeAttempt.started_at.desc()).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active challenge attempt found. Start the challenge first."
        )

    # Get sandbox from stored attempt data
    sandbox_manager = get_sandbox_manager()
    sandbox_id = attempt.commands_used.get('_sandbox_id') if attempt.commands_used else None

    if not sandbox_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge session not found. Please restart the challenge."
        )

    sandbox = sandbox_manager.get_sandbox(sandbox_id)
    if not sandbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sandbox session expired. Please restart the challenge."
        )

    try:
        # Execute submitted commands in sandbox
        for command in request.commands_used:
            try:
                sandbox.execute_command(command)
            except Exception as e:
                # Continue even if command fails - validation will catch issues
                pass

        # Validate solution against success criteria
        validation_result = sandbox.validate_success_criteria(challenge.success_criteria)

        # Calculate score based on validation
        if validation_result['success']:
            score = challenge.max_score
        else:
            # Partial credit based on criteria met
            total = validation_result['total_criteria']
            met = validation_result['met_count']
            score = int((met / total) * challenge.max_score) if total > 0 else 0

        # Build feedback message
        feedback_parts = []
        if validation_result['success']:
            feedback_parts.append("✅ Challenge completed successfully!")
        else:
            feedback_parts.append("❌ Challenge incomplete.")

        feedback_parts.append(f"\n\n📊 Criteria: {validation_result['met_count']}/{validation_result['total_criteria']} met")

        if validation_result['criteria_met']:
            feedback_parts.append("\n\n✓ Completed:")
            for criterion in validation_result['criteria_met']:
                feedback_parts.append(f"  • {criterion}")

        if validation_result['criteria_failed']:
            feedback_parts.append("\n\n✗ Missing:")
            for criterion in validation_result['criteria_failed']:
                feedback_parts.append(f"  • {criterion}")

        feedback = "\n".join(feedback_parts)

        # Update attempt record
        attempt.completed_at = datetime.utcnow()
        attempt.success = validation_result['success']
        attempt.commands_used = request.commands_used
        attempt.score = score
        attempt.time_taken_seconds = request.time_taken_seconds
        attempt.hints_used = request.hints_used

        # Award XP if successful
        if validation_result['success']:
            # Calculate XP: base score minus penalties for hints and time
            xp_earned = score
            hint_penalty = request.hints_used * 5
            time_penalty = 0

            if challenge.time_limit_seconds and request.time_taken_seconds > challenge.time_limit_seconds:
                time_penalty = 10

            xp_earned = max(0, xp_earned - hint_penalty - time_penalty)
            current_player.total_xp += xp_earned

        db.commit()
        db.refresh(attempt)

    finally:
        # Clean up sandbox
        sandbox_manager.cleanup_sandbox(sandbox_id)

    return ChallengeAttemptResponse(
        id=attempt.id,
        player_id=attempt.player_id,
        challenge_id=attempt.challenge_id,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        success=attempt.success,
        commands_used=attempt.commands_used,
        score=attempt.score,
        time_taken_seconds=attempt.time_taken_seconds,
        hints_used=attempt.hints_used,
        feedback=feedback
    )


@router.get("/{challenge_id}/attempts", response_model=List[ChallengeAttemptResponse])
async def get_my_challenge_attempts(
    challenge_id: str,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get current player's attempts for a specific challenge
    """
    attempts = db.query(ChallengeAttempt).filter(
        ChallengeAttempt.player_id == current_player.id,
        ChallengeAttempt.challenge_id == challenge_id
    ).order_by(ChallengeAttempt.started_at.desc()).all()

    return [
        ChallengeAttemptResponse(
            id=attempt.id,
            player_id=attempt.player_id,
            challenge_id=attempt.challenge_id,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            success=attempt.success,
            commands_used=attempt.commands_used,
            score=attempt.score,
            time_taken_seconds=attempt.time_taken_seconds,
            hints_used=attempt.hints_used,
            feedback=None
        )
        for attempt in attempts
    ]


@router.get("/{challenge_id}/leaderboard", response_model=List[ChallengeLeaderboardEntry])
async def get_challenge_leaderboard(
    challenge_id: str,
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    db: Session = Depends(get_db)
):
    """
    Get leaderboard for a specific challenge

    Returns top players ranked by score (desc) and time (asc)
    """
    # Check if challenge exists
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge '{challenge_id}' not found"
        )

    # Get best attempt for each player
    subquery = db.query(
        ChallengeAttempt.player_id,
        func.max(ChallengeAttempt.score).label('best_score'),
        func.min(ChallengeAttempt.time_taken_seconds).label('best_time')
    ).filter(
        ChallengeAttempt.challenge_id == challenge_id,
        ChallengeAttempt.success == True
    ).group_by(ChallengeAttempt.player_id).subquery()

    # Join with players to get usernames
    leaderboard_query = db.query(
        Player.username,
        subquery.c.best_score,
        subquery.c.best_time,
        ChallengeAttempt.completed_at
    ).join(
        subquery, Player.id == subquery.c.player_id
    ).join(
        ChallengeAttempt,
        (ChallengeAttempt.player_id == Player.id) &
        (ChallengeAttempt.challenge_id == challenge_id) &
        (ChallengeAttempt.score == subquery.c.best_score)
    ).order_by(
        subquery.c.best_score.desc(),
        subquery.c.best_time.asc()
    ).limit(limit).all()

    # Add rank
    leaderboard = []
    for rank, (username, score, time, completed_at) in enumerate(leaderboard_query, start=1):
        leaderboard.append(
            ChallengeLeaderboardEntry(
                player_username=username,
                score=score,
                time_taken_seconds=time,
                completed_at=completed_at,
                rank=rank
            )
        )

    return leaderboard


@router.get("/{challenge_id}/stats", response_model=ChallengeStatsResponse)
async def get_challenge_stats(
    challenge_id: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific challenge
    """
    # Check if challenge exists
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge '{challenge_id}' not found"
        )

    # Calculate stats
    attempts = db.query(ChallengeAttempt).filter(
        ChallengeAttempt.challenge_id == challenge_id
    ).all()

    total_attempts = len(attempts)
    successful_attempts = sum(1 for a in attempts if a.success)
    success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0.0

    completed_attempts = [a for a in attempts if a.completed_at is not None]
    average_score = sum(a.score for a in completed_attempts) / len(completed_attempts) if completed_attempts else 0.0
    average_time = sum(a.time_taken_seconds or 0 for a in completed_attempts) / len(completed_attempts) if completed_attempts else 0.0
    fastest_time = min((a.time_taken_seconds for a in completed_attempts if a.time_taken_seconds), default=None)

    return ChallengeStatsResponse(
        challenge_id=challenge_id,
        total_attempts=total_attempts,
        successful_attempts=successful_attempts,
        success_rate=success_rate,
        average_score=average_score,
        average_time_seconds=average_time,
        fastest_time_seconds=fastest_time
    )
