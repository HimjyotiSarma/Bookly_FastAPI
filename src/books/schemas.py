from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import uuid
from src.reviews.schema import ReviewModal
from src.tags.schemas import TagCreateModal


class Book(BaseModel):
    uid: uuid.UUID
    Title: str
    Author: str
    Publication_Year: date
    Genre: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookDetailModal(Book):
    reviews: List[ReviewModal]
    tags: List[TagCreateModal]

    class Config:
        from_attributes = True


class BookUpdate(BaseModel):
    Title: Optional[str] = None
    Author: Optional[str] = None
    Publication_Year: Optional[str] = None
    Genre: Optional[List[str]] = None


class BookCreate(BaseModel):
    Title: str
    Author: str
    Publication_Year: str
    Genre: List[str]


class BookTags(Book):
    tags: List[TagCreateModal]
