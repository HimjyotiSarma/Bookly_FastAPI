from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import AccessTokenBearer, RoleChecker, get_current_user
from src.db.models import User
from src.db.main import get_session
from .service import ReviewService
from .schema import ReviewCreate, ReviewModal

reviews_router = APIRouter()
access_token_bearer = AccessTokenBearer()

review_service = ReviewService()

admin_checker = Depends(RoleChecker(["admin"]))
user_checker = Depends(RoleChecker(["user"]))
all_user_checker = Depends(RoleChecker(["admin", "user"]))


@reviews_router.post(
    "/book/{book_uid}", dependencies=[all_user_checker], response_model=ReviewModal
)
async def add_book_review(
    book_uid: str,
    review_data: ReviewCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user_email = current_user.email

    new_review = await review_service.add_review_to_book(
        user_email, book_uid, review_data, session
    )

    return new_review
