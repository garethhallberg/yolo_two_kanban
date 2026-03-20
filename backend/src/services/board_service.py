from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func

from ..database.models import KanbanBoard, User, KanbanColumn
from ..schemas.board import BoardCreate, BoardUpdate


class BoardService:
    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[KanbanBoard]:
        """Get board by user ID"""
        return db.query(KanbanBoard).filter(KanbanBoard.user_id == user_id).first()

    @staticmethod
    def get_by_id(db: Session, board_id: int) -> Optional[KanbanBoard]:
        """Get board by ID"""
        return db.query(KanbanBoard).filter(KanbanBoard.id == board_id).first()

    @staticmethod
    def create_board(db: Session, user_id: int, board_data: BoardCreate) -> KanbanBoard:
        """Create a new board for user"""
        board = KanbanBoard(
            user_id=user_id,
            title=board_data.title,
            updated_at=func.now()  # Set updated_at to current time on creation
        )
        db.add(board)
        db.commit()
        db.refresh(board)
        return board

    @staticmethod
    def update_board(db: Session, board_id: int, board_data: BoardUpdate) -> Optional[KanbanBoard]:
        """Update existing board"""
        board = db.query(KanbanBoard).filter(KanbanBoard.id == board_id).first()
        if not board:
            return None
        
        for key, value in board_data.model_dump(exclude_unset=True).items():
            setattr(board, key, value)
            
        db.commit()
        db.refresh(board)
        return board

    @staticmethod
    def delete_board(db: Session, board_id: int) -> bool:
        """Delete board by ID"""
        board = db.query(KanbanBoard).filter(KanbanBoard.id == board_id).first()
        if not board:
            return False
        
        db.delete(board)
        db.commit()
        return True

    @staticmethod
    def get_board_with_columns_and_cards(db: Session, user_id: int) -> Optional[KanbanBoard]:
        """Get board with all columns and cards (eager loading)"""
        return (
            db.query(KanbanBoard)
            .filter(KanbanBoard.user_id == user_id)
            .options(
                joinedload(KanbanBoard.columns).joinedload(KanbanColumn.cards)
            )
            .first()
        )
