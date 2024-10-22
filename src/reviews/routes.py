from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
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


@reviews_router.get(
    "/{review_uid}", dependencies=[all_user_checker], response_model=ReviewModal
)
async def get_review_by_uid(
    review_uid: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user_uid = current_user.uid

    get_review = await review_service.get_review_by_uid(review_uid, user_uid, session)
    return get_review


@reviews_router.get("/", dependencies=[admin_checker], response_model=List[ReviewModal])
async def get_all_reviews(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(access_token_bearer),
):
    get_all_reviews = await review_service.get_all_reviews(session)
    return get_all_reviews


@reviews_router.delete("/{review_uid}", dependencies=[all_user_checker])
async def delete_book_review(
    review_uid: str,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(access_token_bearer),
):
    print(token_data)
    user_uid = token_data.get("user")["user_uid"]
    if not user_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Token not found. Please Login",
        )

    delete_review_data = await review_service.delete_user_review(
        review_uid, user_uid, session
    )
    return JSONResponse(content=delete_review_data, status_code=status.HTTP_200_OK)
