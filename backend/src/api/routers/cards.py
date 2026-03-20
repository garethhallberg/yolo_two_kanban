"""
Card management endpoints for Kanban application.
"""
import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...config.settings import Settings
from ...database.connection import get_db
from ...database.models import User
from ...schemas.card import CardCreate, CardResponse, CardUpdate, CardMove
from ...services.board_service import BoardService
from ...services.column_service import ColumnService
from ...services.card_service import CardService
from ...api.routers.auth import get_current_user

settings = Settings()
logger = logging.getLogger(__name__)

router = APIRouter(tags=["cards"])


@router.post("/", response_model=CardResponse)
def create_card(
    card_data: CardCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Create a new card in a column"""
    logger.info(f"[BACKEND] Creating card in column {card_data.column_id}")
    
    # Get column
    column = ColumnService.get_by_id(db, card_data.column_id)
    if not column:
        logger.warning(f"[BACKEND] Column not found with id={card_data.column_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found"
        )
    
    # Verify column belongs to user's board
    if column.board.user_id != current_user.id:
        logger.warning(f"[BACKEND] User {current_user.id} trying to create card in column {card_data.column_id} from different board")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create card in this column"
        )
    
    # Create card
    card = CardService.create_card(db, card_data.column_id, card_data)
    logger.info(f"[BACKEND] Created card with id={card.id}")
    
    return card


@router.put("/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    card_data: CardUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update an existing card"""
    logger.info(f"[BACKEND] Updating card with id={card_id}")
    
    # Get card
    card = CardService.get_by_id(db, card_id)
    if not card:
        logger.warning(f"[BACKEND] Card not found with id={card_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Verify card belongs to user's board
    if card.column.board.user_id != current_user.id:
        logger.warning(f"[BACKEND] User {current_user.id} trying to update card {card_id} from different board")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this card"
        )
    
    # Update card
    updated_card = CardService.update_card(db, card_id, card_data)
    if not updated_card:
        logger.error(f"[BACKEND] Failed to update card with id={card_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update card"
        )
    
    logger.info(f"[BACKEND] Successfully updated card with id={updated_card.id}")
    return updated_card


@router.delete("/{card_id}", response_model=CardResponse)
def delete_card(
    card_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Delete a card"""
    logger.info(f"[BACKEND] Deleting card with id={card_id}")
    
    # Get card
    card = CardService.get_by_id(db, card_id)
    if not card:
        logger.warning(f"[BACKEND] Card not found with id={card_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Verify card belongs to user's board
    if card.column.board.user_id != current_user.id:
        logger.warning(f"[BACKEND] User {current_user.id} trying to delete card {card_id} from different board")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this card"
        )
    
    # Delete card
    success = CardService.delete_card(db, card_id)
    if not success:
        logger.error(f"[BACKEND] Failed to delete card with id={card_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete card"
        )
    
    logger.info(f"[BACKEND] Successfully deleted card with id={card_id}")
    return card


@router.put("/{card_id}/move", response_model=CardResponse)
def move_card(
    card_id: int,
    move_data: CardMove,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Move card to different column and/or position"""
    new_column_id = move_data.to_column_id
    new_position = move_data.new_position
    logger.info(f"[BACKEND] Moving card {card_id} to column {new_column_id} at position {new_position}")
    
    # Get card
    card = CardService.get_by_id(db, card_id)
    if not card:
        logger.warning(f"[BACKEND] Card not found with id={card_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Verify card belongs to user's board
    if card.column.board.user_id != current_user.id:
        logger.warning(f"[BACKEND] User {current_user.id} trying to move card {card_id} from different board")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to move this card"
        )
    
    # Get new column
    new_column = ColumnService.get_by_id(db, new_column_id)
    if not new_column:
        logger.warning(f"[BACKEND] New column not found with id={new_column_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="New column not found"
        )
    
    # Verify new column belongs to same board
    if new_column.board_id != card.column.board_id:
        logger.warning(f"[BACKEND] Cannot move card {card_id} to column {new_column_id} from different board")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot move card to column from different board"
        )
    
    # Move card
    moved_card = CardService.move_card(db, card_id, new_column_id, new_position)
    if not moved_card:
        logger.error(f"[BACKEND] Failed to move card with id={card_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to move card"
        )
    
    logger.info(f"[BACKEND] Successfully moved card {card_id} to column {new_column_id} at position {new_position}")
    return moved_card


@router.put("/{card_id}/reorder", response_model=CardResponse)
def reorder_card(
    card_id: int,
    new_position: float,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Reorder a card within its column"""
    logger.info(f"[BACKEND] Reordering card {card_id} to position {new_position}")
    
    # Get card
    card = CardService.get_by_id(db, card_id)
    if not card:
        logger.warning(f"[BACKEND] Card not found with id={card_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Verify card belongs to user's board
    if card.column.board.user_id != current_user.id:
        logger.warning(f"[BACKEND] User {current_user.id} trying to reorder card {card_id} from different board")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reorder this card"
        )
    
    # Reorder card
    reordered_card = CardService.reorder_card(db, card_id, new_position)
    if not reordered_card:
        logger.error(f"[BACKEND] Failed to reorder card with id={card_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder card"
        )
    
    logger.info(f"[BACKEND] Successfully reordered card {card_id} to position {new_position}")
    return reordered_card


@router.get("/column/{column_id}", response_model=List[CardResponse])
def get_cards_by_column(
    column_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get all cards for a specific column"""
    logger.info(f"[BACKEND] Getting cards for column_id={column_id}")
    
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
    
    # Get cards
    cards = CardService.get_by_column(db, column_id)
    logger.info(f"[BACKEND] Found {len(cards)} cards for column_id={column_id}")
    
    return cards
