from fastapi import APIRouter, Depends, dependencies, HTTPException, status
from .schemas import TagAddModal, TagCreateModal, TagModal
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.books.schemas import BookTags
from .service import TagService
from src.auth.dependencies import AccessTokenBearer, get_current_user, RoleChecker
from typing import List
from fastapi.responses import JSONResponse

tag_router = APIRouter()
tag_service = TagService()
access_token_bearer = AccessTokenBearer()

admin_checker = Depends(RoleChecker(["admin"]))
user_checker = Depends(RoleChecker(["user"]))
user_admin_checker = Depends(RoleChecker(["user", "admin"]))


@tag_router.get("/", response_model=List[TagModal], dependencies=[admin_checker])
async def get_all_tags(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(access_token_bearer),
):
    all_tags = await tag_service.get_all_tags(session)
    return all_tags


@tag_router.post("/add", response_model=TagModal, dependencies=[user_admin_checker])
async def add_tag(
    tag_data: TagCreateModal, session: AsyncSession = Depends(get_session)
):
    create_tag = await tag_service.add_tag(tag_data, session)
    return create_tag


@tag_router.post(
    "/book/{book_uid}/tags", response_model=BookTags, dependencies=[user_admin_checker]
)
async def add_tags_to_book(
    book_uid: str, tag_data: TagAddModal, session: AsyncSession = Depends(get_session)
):
    book_with_tag = await tag_service.add_tag_to_book(tag_data, book_uid, session)
    return book_with_tag


@tag_router.put(
    "/{tag_uid}", response_model=TagModal, dependencies=[user_admin_checker]
)
async def update_tag(
    tag_uid: str,
    tag_update_data: TagCreateModal,
    session: AsyncSession = Depends(get_session),
):
    update_tag_info = await tag_service.update_tag(tag_uid, tag_update_data, session)
    return update_tag_info


@tag_router.delete("/{tag_uid}", dependencies=[user_admin_checker])
async def delete_tag(tag_uid: str, session: AsyncSession = Depends(get_session)):
    delete_tag_info = await tag_service.delete_tag(tag_uid, session)
    return delete_tag_info
