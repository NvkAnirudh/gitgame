"""
Sandbox API Endpoints - Interactive Terminal Backend
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.git_sandbox import get_sandbox_manager
from app.models.content import Lesson, Challenge
from app.models.player import Player
from app.core.dependencies import get_current_player

router = APIRouter(prefix="/sandbox", tags=["sandbox"])


class SandboxCreateRequest(BaseModel):
    lesson_id: Optional[str] = None
    challenge_id: Optional[str] = None


class SandboxCreateResponse(BaseModel):
    sandbox_id: str
    initialized: bool
    message: str


class SandboxExecuteRequest(BaseModel):
    command: str


class SandboxExecuteResponse(BaseModel):
    output: str
    success: bool
    execution_time_ms: float


@router.post("/create", response_model=SandboxCreateResponse)
async def create_sandbox(
    request: SandboxCreateRequest,
    db: Session = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    """
    Create a new Git sandbox for interactive terminal use.
    Optionally initialize with git_state from a lesson or challenge.
    """
    try:
        sandbox_manager = get_sandbox_manager()
        git_state = None

        # Load git_state from challenge or lesson if provided
        if request.challenge_id:
            challenge = db.query(Challenge).filter(
                Challenge.id == request.challenge_id
            ).first()
            if challenge and challenge.git_state:
                git_state = challenge.git_state

        elif request.lesson_id:
            lesson = db.query(Lesson).filter(
                Lesson.id == request.lesson_id
            ).first()
            # Lessons might have associated challenges with git_state
            if lesson:
                challenge = db.query(Challenge).filter(
                    Challenge.lesson_id == request.lesson_id
                ).first()
                if challenge and challenge.git_state:
                    git_state = challenge.git_state

        # Create sandbox
        sandbox = sandbox_manager.create_sandbox(git_state=git_state)

        return SandboxCreateResponse(
            sandbox_id=sandbox.sandbox_id,
            initialized=True,
            message="Sandbox created successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create sandbox: {str(e)}"
        )


@router.post("/{sandbox_id}/execute", response_model=SandboxExecuteResponse)
async def execute_command(
    sandbox_id: str,
    request: SandboxExecuteRequest,
    current_player: Player = Depends(get_current_player)
):
    """
    Execute a Git command in the specified sandbox.
    """
    try:
        sandbox_manager = get_sandbox_manager()
        sandbox = sandbox_manager.get_sandbox(sandbox_id)

        if not sandbox:
            raise HTTPException(
                status_code=404,
                detail="Sandbox not found or expired"
            )

        # Execute command
        result = sandbox.execute_command(request.command)

        return SandboxExecuteResponse(
            output=result.get('output', ''),
            success=result.get('success', False),
            execution_time_ms=result.get('execution_time', 0)
        )

    except ValueError as e:
        # Command blocked or invalid
        return SandboxExecuteResponse(
            output=str(e),
            success=False,
            execution_time_ms=0
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Command execution failed: {str(e)}"
        )


@router.post("/{sandbox_id}/cleanup")
async def cleanup_sandbox(
    sandbox_id: str,
    current_player: Player = Depends(get_current_player)
):
    """
    Cleanup and destroy a sandbox.
    """
    try:
        sandbox_manager = get_sandbox_manager()
        sandbox_manager.destroy_sandbox(sandbox_id)

        return {"success": True, "message": "Sandbox cleaned up"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup sandbox: {str(e)}"
        )


@router.get("/{sandbox_id}/status")
async def get_sandbox_status(
    sandbox_id: str,
    current_player: Player = Depends(get_current_player)
):
    """
    Get the current state of a sandbox.
    """
    try:
        sandbox_manager = get_sandbox_manager()
        sandbox = sandbox_manager.get_sandbox(sandbox_id)

        if not sandbox:
            raise HTTPException(
                status_code=404,
                detail="Sandbox not found"
            )

        # Get git status
        status_result = sandbox.execute_command("git status")

        return {
            "sandbox_id": sandbox_id,
            "exists": True,
            "git_status": status_result.get('output', '')
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sandbox status: {str(e)}"
        )
