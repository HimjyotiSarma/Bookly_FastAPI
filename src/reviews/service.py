from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from src.db.models import Review, User
from sqlmodel import select, update, delete, desc
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
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User data not found"
                )

            review_data_dict = review_data.model_dump()
            review_data_dict["user_uid"] = user_data.uid
            review_data_dict["book_uid"] = book_data.uid
            new_review = Review(**review_data_dict)
            new_review.book = book_data
            new_review.user = user_data

            session.add(new_review)
            await session.commit()
            return new_review
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Review Create Error: {str(e)}",
            )

    async def get_review_by_uid(
        self, review_uid: str, user_uid: str, session: AsyncSession
    ):
        try:
            user_data: User = await user_service.get_user_by_uid(user_uid, session)
            statement = (
                select(Review)
                .where(Review.uid == review_uid)
                .where(Review.user_uid == user_uid)
            )
            if user_data.role == "admin":
                statement = select(Review).where(Review.uid == review_uid)

            result = await session.exec(statement)
            return result.first()

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error getting review: {str(e)}",
            )

    async def get_all_reviews(
        self, session: AsyncSession, limit: int = 100, offset: int = 0
    ):
        try:
            statement = (
                select(Review)
                .order_by(desc(Review.created_at))
                .limit(limit)
                .offset(offset)
            )
            result = await session.exec(statement)
            return result.all()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error getting review: {str(e)}",
            )

    async def delete_user_review(
        self, review_uid: str, user_uid: str, session: AsyncSession
    ):
        try:
            review_to_delete: Review = await self.get_review_by_uid(
                review_uid, user_uid, session
            )
            if review_to_delete is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Review Not found in Database. Please Search Again",
                )

            await session.delete(review_to_delete)
            await session.commit()
            return {"detail": "Review deleted successfully"}

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting review: {str(e)}",
            )
