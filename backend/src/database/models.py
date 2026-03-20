from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from typing import List

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to KanbanBoard (one-to-one)
    board = relationship("KanbanBoard", back_populates="user", uselist=False)


class KanbanBoard(Base):
    __tablename__ = "kanban_boards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    title = Column(String(100), nullable=False, default="My Kanban Board")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="board")
    columns = relationship("KanbanColumn", back_populates="board", 
                           cascade="all, delete-orphan", order_by="KanbanColumn.position")


class KanbanColumn(Base):
    __tablename__ = "kanban_columns"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("kanban_boards.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    position = Column(Float, nullable=False)
    color = Column(String(20), nullable=True)
    wip_limit = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    board = relationship("KanbanBoard", back_populates="columns")
    cards = relationship("KanbanCard", back_populates="column",
                       cascade="all, delete-orphan", order_by="KanbanCard.position")


class KanbanCard(Base):
    __tablename__ = "kanban_cards"

    id = Column(Integer, primary_key=True, index=True)
    column_id = Column(Integer, ForeignKey("kanban_columns.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    position = Column(Float, nullable=False)
    priority = Column(String(20), nullable=False, default="medium")
    assignee = Column(String(100), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    column = relationship("KanbanColumn", back_populates="cards")