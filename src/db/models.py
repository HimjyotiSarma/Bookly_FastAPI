from sqlmodel import SQLModel, Field, Column, text, Relationship
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import UniqueConstraint
from sqlalchemy.schema import ForeignKey
from typing import List, Optional
from datetime import datetime, date
import uuid

# from src.db import models


class BookTag(SQLModel, table=True):
    book_uid: uuid.UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_uid: uuid.UUID = Field(default=None, foreign_key="tag.uid", primary_key=True)

    __table_args__ = (UniqueConstraint("book_uid", "tag_uid", name="unique_book_tag"),)


class Book(SQLModel, table=True):
    __tablename__ = "books"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    )
    Title: str
    Author: str
    Publication_Year: date
    user_uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, ForeignKey("users.uid", ondelete="CASCADE"), nullable=False
        )
    )
    Genre: List[str] = Field(sa_column=Column(pg.ARRAY(pg.VARCHAR), nullable=True))
    user: Optional["User"] = Relationship(back_populates="books")
    tags: List["Tag"] = Relationship(
        back_populates="books",
        link_model=BookTag,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), nullable=False, default=datetime.now
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now,
            onupdate=datetime.now,
        )
    )

    __table_args__ = (
        UniqueConstraint("Title", "Author", "user_uid", name="unique_title_author"),
    )

    def __repr__(self) -> str:
        return f"<Book {self.Title} of {self.Author}>"


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str = Field(
        sa_column=Column(pg.VARCHAR(100), nullable=False, unique=True)
    )
    email: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False, unique=True))
    firstname: str = Field(sa_column=Column(pg.VARCHAR(50), nullable=False))
    lastname: str = Field(
        sa_column=Column(
            pg.VARCHAR(50),
            nullable=False,
        )
    )
    is_verified: bool = Field(
        sa_column=Column(pg.BOOLEAN, nullable=False, default=False)
    )
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    role: str = Field(
        sa_column=Column(pg.VARCHAR(20), nullable=False, server_default=text("'user'"))
    )
    password_hash: str = Field(
        sa_column=Column(
            pg.VARCHAR(255),
            nullable=False,
            unique=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), nullable=False, default=datetime.now
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now,
            onupdate=datetime.now,
        )
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    rating: int = Field(
        ge=1,
        le=5,
        sa_column=Column(
            pg.INTEGER,
            nullable=False,
        ),
    )
    review_text: str = Field(
        min_length=5, sa_column=Column(pg.VARCHAR(250), nullable=False)
    )
    user_uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, ForeignKey("users.uid", ondelete="CASCADE"), nullable=False
        )
    )
    book_uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID, ForeignKey("books.uid", ondelete="CASCADE"), nullable=False
        )
    )
    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["Book"] = Relationship(back_populates="reviews")
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True), nullable=False, default=datetime.now
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now,
            onupdate=datetime.now,
        )
    )

    def __repr__(self) -> str:
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"


class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR(240), nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        back_populates="tags",
        link_model=BookTag,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"
