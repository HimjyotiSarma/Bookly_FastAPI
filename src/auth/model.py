from sqlmodel import SQLModel, Field, Column, text, Relationship
from typing import List
import sqlalchemy.dialects.postgresql as pg
import uuid
from sqlalchemy import UniqueConstraint
from src.books import models
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = 'users'
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    username: str = Field(
        sa_column=Column(
            pg.VARCHAR(100),
            nullable=False,
            unique=True
        )
    )
    email: str = Field(
        sa_column=Column(
            pg.VARCHAR(255),
            nullable=False,
            unique=True
        )
    )
    firstname: str = Field(
        sa_column=Column(
            pg.VARCHAR(50),
            nullable=False
        )
    )
    lastname: str = Field(
        sa_column=Column(
            pg.VARCHAR(50),
            nullable=False,
        )
    )
    is_verified: bool = Field(
        sa_column=Column(
            pg.BOOLEAN,
            nullable=False,
            default=False
        )
    )
    books: List["models.Book"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'selectin'})
    role: str = Field(
        sa_column=Column(
            pg.VARCHAR(20),
            nullable=False,
            server_default=text("'user'")
        )
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
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            default = datetime.now
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



    def __repr__(self):
        return f"<User {self.username}>"


