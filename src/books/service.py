from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status, Depends
from sqlmodel import select, desc, delete
from sqlalchemy.orm import selectinload
from src.db.models import Book
from src.reviews.schema import ReviewModal
from .schemas import BookCreate, BookUpdate
from datetime import datetime
from src.auth.dependencies import AccessTokenBearer
import uuid

access_token = AccessTokenBearer()


class BooksService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        print("USER ID : ", user_uid)
        try:
            statement = (
                select(Book)
                .where(Book.user_uid == user_uid)
                .order_by(desc(Book.created_at))
            )
            result = await session.exec(statement)
            return result.all()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error getting User books : {str(e)}",
            )

    async def get_single_book(self, book_id: str, session: AsyncSession):
        try:
            statement = (
                select(Book)
                .where(Book.uid == book_id)
                .options(selectinload(Book.reviews))
            )
            result = await session.exec(statement)
            book = result.first()

            return book
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error getting Book : {str(e)}",
            )

    async def create_book(
        self, book_data: BookCreate, user_uuid: str, session: AsyncSession
    ):
        try:
            book_data_dict = book_data.model_dump()
            book_data_dict["user_uid"] = user_uuid
            print("BOOK DATA DICT : ", book_data_dict)
            new_book = Book(**book_data_dict)
            new_book.Publication_Year = datetime.strptime(
                book_data_dict["Publication_Year"], "%Y-%m-%d"
            )
            session.add(new_book)
            await session.commit()
            await session.refresh(new_book)
            return new_book
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error Creating Book: {str(e)}",
            )

    async def update_book(
        self, book_uid: str, update_book: BookUpdate, session: AsyncSession
    ):
        try:
            book_to_update = await self.get_single_book(book_uid, session)
            if book_to_update is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book Not found in Database. Please Search Again",
                )

            update_book_dict = update_book.model_dump()

            if "Publication_Year" in update_book_dict and isinstance(
                update_book_dict["Publication_Year"], str
            ):
                update_book_dict["Publication_Year"] = datetime.strptime(
                    update_book_dict["Publication_Year"], "%Y-%m-%d"
                ).date()

            for key, value in update_book_dict.items():
                setattr(book_to_update, key, value)
            await session.commit()
            await session.refresh(book_to_update)
            return book_to_update
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error updating book: {str(e)}",
            )

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_single_book(book_uid, session)
        if book_to_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book Not found in Database. Please Search Again",
            )
        try:
            await session.delete(book_to_delete)
            await session.commit()
            return {"detail": "Book deleted successfully"}
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error deleting book: {str(e)}",
            )
