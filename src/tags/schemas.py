from pydantic import BaseModel
from datetime import datetime
from typing import List
import uuid


class TagModal(BaseModel):
    uid: uuid.UUID
    name: str
    created_at: datetime


class TagCreateModal(BaseModel):
    name: str


class TagAddModal(BaseModel):
    tags: List[TagCreateModal]
