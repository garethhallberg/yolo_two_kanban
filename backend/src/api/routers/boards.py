"""
Board management endpoints for Kanban application.
"""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...config.settings import Settings
from ...database.connection import get_db
from ...database.models import User
from ...schemas.board import BoardCreate, BoardResponse, BoardUpdate
from ...services.board_service import BoardService
from ...api.routers.auth import get_current_user

settings = Settings()
logger = logging.getLogger(__name__)

router = APIRouter(tags=["boards"])


@router.get("/", response_model=BoardResponse)
def get_user_board(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get the current user's Kanban board"""
    logger.info(f"[BACKEND] Getting board for user_id={current_user.id}")
    
    board = BoardService.get_by_user_id(db, current_user.id)
    
    if not board:
        logger.info(f"[BACKEND] No board found for user_id={current_user.id}, creating default board")
        # Create default board for user
        default_board = BoardCreate(title="My Kanban Board")
        board = BoardService.create_board(db, current_user.id, default_board)
        logger.info(f"[BACKEND] Created default board with id={board.id}")
    
    logger.info(f"[BACKEND] Returning board with id={board.id}")
    return board


@router.put("/", response_model=BoardResponse)
def update_board(
    board_data: BoardUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update the current user's Kanban board"""
    logger.info(f"[BACKEND] Updating board for user_id={current_user.id}")
    
    # Get user's board
    board = BoardService.get_by_user_id(db, current_user.id)
    if not board:
        logger.warning(f"[BACKEND] No board found for user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Update board
    updated_board = BoardService.update_board(db, board.id, board_data)
    if not updated_board:
        logger.error(f"[BACKEND] Failed to update board with id={board.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update board"
        )
    
    logger.info(f"[BACKEND] Successfully updated board with id={updated_board.id}")
    return updated_board


@router.get("/full", response_model=BoardResponse)
def get_full_board(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get the current user's full Kanban board with columns and cards"""
    logger.info(f"[BACKEND] Getting full board for user_id={current_user.id}")
    
    board = BoardService.get_board_with_columns_and_cards(db, current_user.id)
    
    if not board:
        logger.info(f"[BACKEND] No board found for user_id={current_user.id}, creating default board")
        # Create default board for user
        default_board = BoardCreate(title="My Kanban Board")
        board = BoardService.create_board(db, current_user.id, default_board)
        logger.info(f"[BACKEND] Created default board with id={board.id}")
    
    logger.info(f"[BACKEND] Returning full board with id={board.id}")
    return board
