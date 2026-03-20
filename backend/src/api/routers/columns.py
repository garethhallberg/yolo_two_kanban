"""
Column management endpoints for Kanban application.
"""
import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...config.settings import Settings
from ...database.connection import get_db
from ...database.models import User
from ...schemas.column import ColumnCreate, ColumnResponse, ColumnUpdate
from ...services.board_service import BoardService
from ...services.column_service import ColumnService
from ...api.routers.auth import get_current_user

settings = Settings()
logger = logging.getLogger(__name__)

router = APIRouter(tags=["columns"])


@router.post("/", response_model=ColumnResponse)
def create_column(
    column_data: ColumnCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Create a new column on user's board"""
    logger.info(f"[BACKEND] Creating column for user_id={current_user.id}")
    
    # Get user's board
    board = BoardService.get_by_user_id(db, current_user.id)
    if not board:
        logger.warning(f"[BACKEND] No board found for user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Create column
    column = ColumnService.create_column(db, board.id, column_data)
    logger.info(f"[BACKEND] Created column with id={column.id}")
    
    return column


@router.put("/{column_id}", response_model=ColumnResponse)
def update_column(
    column_id: int,
    column_data: ColumnUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update an existing column"""
    logger.info(f"[BACKEND] Updating column with id={column_id}")
    
    # Get column
    column = ColumnService.get_by_id(db, column_id)
    if not column:
        logger.warning(f"[BACKEND] Column not found with id={column_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Verify column belongs to user's board
    if column.board.user_id != current_user.id:
        logger.warning(f"[BACKEND] User {current_user.id} trying to access column {column_id} from different board")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this column"
        )
    
    # Update column
    updated_column = ColumnService.update_column(db, column_id, column_data)
    if not updated_column:
        logger.error(f"[BACKEND] Failed to update column with id={column_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update column"
        )
    
    logger.info(f"[BACKEND] Successfully updated column with id={updated_column.id}")
    return updated_column


@router.delete("/{column_id}", response_model=ColumnResponse)
def delete_column(
    column_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Delete a column"""
    logger.info(f"[BACKEND] Deleting column with id={column_id}")
    
    # Get column
    column = ColumnService.get_by_id(db, column_id)
    if not column:
        logger.warning(f"[BACKEND] Column not found with id={column_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Verify column belongs to user's board
    if column.board.user_id != current_user.id:
        logger.warning(f"[BACKEND] User {current_user.id} trying to delete column {column_id} from different board")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this column"
        )
    
    # Delete column
    success = ColumnService.delete_column(db, column_id)
    if not success:
        logger.error(f"[BACKEND] Failed to delete column with id={column_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete column"
        )
    
    logger.info(f"[BACKEND] Successfully deleted column with id={column_id}")
    return column


@router.put("/{column_id}/reorder", response_model=ColumnResponse)
def reorder_column(
    column_id: int,
    new_position: float,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Reorder a column (update its position)"""
    logger.info(f"[BACKEND] Reordering column {column_id} to position {new_position}")
    
    # Get column
    column = ColumnService.get_by_id(db, column_id)
    if not column:
        logger.warning(f"[BACKEND] Column not found with id={column_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Verify column belongs to user's board
    if column.board.user_id != current_user.id:
        logger.warning(f"[BACKEND] User {current_user.id} trying to reorder column {column_id} from different board")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reorder this column"
        )
    
    # Reorder column
    reordered_column = ColumnService.reorder_column(db, column_id, new_position)
    if not reordered_column:
        logger.error(f"[BACKEND] Failed to reorder column with id={column_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder column"
        )
    
    logger.info(f"[BACKEND] Successfully reordered column {column_id} to position {new_position}")
    return reordered_column


@router.get("/board/{board_id}", response_model=List[ColumnResponse])
def get_columns_by_board(
    board_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get all columns for a specific board"""
    logger.info(f"[BACKEND] Getting columns for board_id={board_id}")
    
    # Verify board belongs to user
    board = BoardService.get_by_id(db, board_id)
    if not board:
        logger.warning(f"[BACKEND] Board not found with id={board_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    if board.user_id != current_user.id:
        logger.warning(f"[BACKEND] User {current_user.id} trying to access board {board_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this board"
        )
    
    # Get columns
    columns = ColumnService.get_by_board(db, board_id)
    logger.info(f"[BACKEND] Found {len(columns)} columns for board_id={board_id}")
    
    return columns
