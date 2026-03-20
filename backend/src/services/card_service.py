from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..database.models import KanbanCard, KanbanColumn
from ..schemas.card import CardCreate, CardUpdate


class CardService:
    @staticmethod
    def get_by_id(db: Session, card_id: int) -> Optional[KanbanCard]:
        """Get card by ID"""
        return db.query(KanbanCard).filter(KanbanCard.id == card_id).first()

    @staticmethod
    def get_by_column(db: Session, column_id: int) -> List[KanbanCard]:
        """Get all cards for a column, ordered by position"""
        return (
            db.query(KanbanCard)
            .filter(KanbanCard.column_id == column_id)
            .order_by(KanbanCard.position.asc())
            .all()
        )

    @staticmethod
    def create_card(db: Session, column_id: int, card_data: CardCreate) -> KanbanCard:
        """Create a new card in column"""
        # Find the highest position in this column
        max_position = db.query(
            func.max(KanbanCard.position)
        ).filter(KanbanCard.column_id == column_id).scalar() or 0
        
        # Set new position
        new_position = max_position + 1.0
        
        card = KanbanCard(
            column_id=column_id,
            title=card_data.title,
            description=card_data.description,
            position=new_position,
            priority=card_data.priority,
            assignee=card_data.assignee,
            due_date=card_data.due_date,
            tags=card_data.tags
        )
        db.add(card)
        db.commit()
        db.refresh(card)
        return card

    @staticmethod
    def update_card(db: Session, card_id: int, card_data: CardUpdate) -> Optional[KanbanCard]:
        """Update existing card"""
        card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
        if not card:
            return None
        
        for key, value in card_data.model_dump(exclude_unset=True).items():
            setattr(card, key, value)
            
        db.commit()
        db.refresh(card)
        return card

    @staticmethod
    def delete_card(db: Session, card_id: int) -> bool:
        """Delete card by ID"""
        card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
        if not card:
            return False
        
        db.delete(card)
        db.commit()
        return True

    @staticmethod
    def move_card(db: Session, card_id: int, new_column_id: int, new_position: float) -> Optional[KanbanCard]:
        """Move card to different column and/or position"""
        card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
        if not card:
            return None
        
        card.column_id = new_column_id
        card.position = new_position
        
        db.commit()
        db.refresh(card)
        return card

    @staticmethod
    def reorder_card(db: Session, card_id: int, new_position: float) -> Optional[KanbanCard]:
        """Update card position within same column"""
        card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
        if not card:
            return None
        
        card.position = new_position
        db.commit()
        db.refresh(card)
        return card
