from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BoardBase(BaseModel):
    title: str

class BoardCreate(BoardBase):
    pass

class BoardUpdate(BoardBase):
    pass

class BoardResponse(BoardBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True