from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

class CardBase(BaseModel):
    title: str
    description: Optional[str] = None
    position: float
    priority: str = "medium"
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

    @field_validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of {valid_priorities}')
        return v

class CardCreate(CardBase):
    column_id: int

class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[float] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None


class CardMove(BaseModel):
    to_column_id: int
    new_position: float

class CardResponse(CardBase):
    id: int
    column_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True