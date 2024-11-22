from pydantic import BaseModel, Field, EmailStr
import uuid
from typing import Optional, List
from src.db.models import Book
from src.reviews.schema import ReviewModal
from datetime import datetime
from enum import Enum

# class RoleEnum(str, Enum):
#     user = "user",
#     admin = "admin"
#     moderator = "moderator"
#     editor = "editor"
#     viewer = "viewer"
#     guest = "guest"


class UserCreateModal(BaseModel):
    firstname: str
    lastname: Optional[str]
    username: str = Field(min_length=5)
    email: EmailStr
    password: str = Field(min_length=5)


class UserResponseModal(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    firstname: str
    lastname: Optional[str]
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserBookModal(UserResponseModal):
    books: List[Book]
    reviews: List[ReviewModal]


class UserLoginModal(BaseModel):
    email: str
    password: str


class EmailModal(BaseModel):
    addresses: list[EmailStr]
    subject: Optional[str] = None
    body: Optional[str] = None


class PasswordResetRequestModal(BaseModel):
    email: EmailStr


class NewPasswordModal(BaseModel):
    password: str
    confirm_password: str
