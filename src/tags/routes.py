from fastapi import APIRouter, Depends, dependencies, HTTPException, status
from .schemas import TagAddModal, TagCreateModal, TagModal
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import TagService
from src.auth.dependencies import AccessTokenBearer, get_current_user

tag_router = APIRouter()
tag_service = TagService()
access_token_bearer = AccessTokenBearer()

# @tag_router.get()
