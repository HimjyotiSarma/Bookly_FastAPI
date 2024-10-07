from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class Review(BaseModel):
    uid: uuid.UUID
    rating: int
    review_text: str
    user_uid: uuid.UUID
    book_uid: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ReviewCreate(BaseModel):
    rating: int
    review_text: str
    user_uid: uuid.UUID
    book_uid: uuid.UUID

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    review_text: Optional[str] = None
    user_uid: uuid.UUID
    book_uid: uuid.UUID

