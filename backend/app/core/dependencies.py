"""
Dependencies for FastAPI routes
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.player import Player

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Optional bearer scheme (doesn't require token)
optional_oauth2_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Usage in routes:
        current_user: User = Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token and get user_id
    user_id = verify_token(token, token_type="access")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_player(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Player:
    """
    Dependency to get current player profile

    Usage in routes:
        current_player: Player = Depends(get_current_player)
    """
    player = db.query(Player).filter(Player.user_id == current_user.id).first()

    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player profile not found"
        )

    return player


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get current user (doesn't raise exception if no token)

    Usage in routes:
        current_user: Optional[User] = Depends(get_optional_current_user)
    """
    if credentials is None:
        return None

    token = credentials.credentials
    user_id = verify_token(token, token_type="access")
    if user_id is None:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        return None

    return user


async def get_optional_current_player(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Optional[Player]:
    """
    Dependency to optionally get current player profile (doesn't require auth)

    Usage in routes:
        current_player: Optional[Player] = Depends(get_optional_current_player)
    """
    if current_user is None:
        return None

    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    return player
