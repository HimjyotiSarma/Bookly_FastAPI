from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from src.db.models import Review
from sqlmodel import select, update, delete
from src.auth.service import UserService
from src.books.service import BooksService
from src.auth.dependencies import AccessTokenBearer
from src.auth.schema import UserBookModal
from pydantic import EmailStr
from .schema import ReviewCreate

user_service = UserService()
book_service = BooksService()


class ReviewService:
    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreate,
        session: AsyncSession,
    ):
        try:
            book_data = await book_service.get_single_book(book_uid, session)
            user_data = await user_service.get_user(user_email, session)

            if not book_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Book data not found"
                )

            review_data_dict = review_data.model_dump()
            review_data_dict["user_uid"] = user_data.uid
            review_data_dict["book_uid"] = book_data.uid
            new_review = Review(**review_data_dict)
            new_review.book = book_data
            new_review.user = user_data

            print("REVIEW DATA:  ", review_data_dict)

            session.add(new_review)
            await session.commit()
            return new_review
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Review Create Error: {str(e)}",
            )
