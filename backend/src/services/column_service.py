from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..database.models import KanbanColumn, KanbanBoard
from ..schemas.column import ColumnCreate, ColumnUpdate


class ColumnService:
    @staticmethod
    def get_by_id(db: Session, column_id: int) -> Optional[KanbanColumn]:
        """Get column by ID"""
        return db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()

    @staticmethod
    def get_by_board(db: Session, board_id: int) -> List[KanbanColumn]:
        """Get all columns for a board, ordered by position"""
        return (
            db.query(KanbanColumn)
            .filter(KanbanColumn.board_id == board_id)
            .order_by(KanbanColumn.position.asc())
            .all()
        )

    @staticmethod
    def create_column(db: Session, board_id: int, column_data: ColumnCreate) -> KanbanColumn:
        """Create a new column for board"""
        # Find the highest position in this board
        max_position = db.query(
            func.max(KanbanColumn.position)
        ).filter(KanbanColumn.board_id == board_id).scalar() or 0
        
        # Set new position
        new_position = max_position + 1.0
        
        column = KanbanColumn(
            board_id=board_id,
            title=column_data.title,
            position=new_position,
            color=column_data.color,
            wip_limit=column_data.wip_limit,
            updated_at=func.now()  # Set updated_at to current time on creation
        )
        db.add(column)
        db.commit()
        db.refresh(column)
        return column

    @staticmethod
    def update_column(db: Session, column_id: int, column_data: ColumnUpdate) -> Optional[KanbanColumn]:
        """Update existing column"""
        column = db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()
        if not column:
            return None
        
        for key, value in column_data.model_dump(exclude_unset=True).items():
            setattr(column, key, value)
            
        db.commit()
        db.refresh(column)
        return column

    @staticmethod
    def delete_column(db: Session, column_id: int) -> bool:
        """Delete column by ID"""
        column = db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()
        if not column:
            return False
        
        db.delete(column)
        db.commit()
        return True

    @staticmethod
    def reorder_column(db: Session, column_id: int, new_position: float) -> Optional[KanbanColumn]:
        """Update column position"""
        column = db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()
        if not column:
            return None
        
        column.position = new_position
        db.commit()
        db.refresh(column)
        return column

    @staticmethod
    def get_column_with_cards(db: Session, column_id: int) -> Optional[KanbanColumn]:
        """Get column with all cards (eager loading)"""
        return (
            db.query(KanbanColumn)
            .filter(KanbanColumn.id == column_id)
            .first()
        )
