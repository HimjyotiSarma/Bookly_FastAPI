from sqlmodel import SQLModel, Field, Column, text, Relationship
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import UniqueConstraint
from sqlalchemy.schema import ForeignKey
from typing import List, Optional
from datetime import datetime, date
from src.auth.model import User
import uuid

class Book(SQLModel, table=True):
    __tablename__="books"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            nullable=False,
            default=uuid.uuid4
        )
    )
    Title: str
    Author: str
    Publication_Year: date
    user_uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            ForeignKey("users.uid", ondelete="SET NULL"),
            nullable=False
        )
    )
    Genre: List[str] = Field(
        sa_column=Column(
            pg.ARRAY(pg.VARCHAR),
            nullable=True
        )
    )
    user: Optional[User] = Relationship(back_populates="books")
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now,
            onupdate=datetime.now
        )
    )

    __table_args__ = (
        UniqueConstraint("Title", "Author", "user_uid", name="unique_title_author"),
    )


    def __repr__(self) -> str:
        return f"<Book {self.Title} of {self.Author}>"