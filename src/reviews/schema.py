from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid


class ReviewModal(BaseModel):
    uid: uuid.UUID
    rating: int
    review_text: str
    user_uid: Optional[uuid.UUID]
    book_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    rating: int
    review_text: str


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    review_text: Optional[str] = None
