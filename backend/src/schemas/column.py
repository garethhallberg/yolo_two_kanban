from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ColumnBase(BaseModel):
    title: str
    position: float
    color: Optional[str] = None
    wip_limit: Optional[int] = None

class ColumnCreate(ColumnBase):
    board_id: int

class ColumnUpdate(BaseModel):
    title: Optional[str] = None
    position: Optional[float] = None
    color: Optional[str] = None
    wip_limit: Optional[int] = None

class ColumnResponse(ColumnBase):
    id: int
    board_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True