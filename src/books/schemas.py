from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class Book(BaseModel):
    uid: uuid.UUID
    Title: str
    Author: str
    Publication_Year: str
    Genre: List[str]
    created_at: datetime
    updated_at: datetime

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

