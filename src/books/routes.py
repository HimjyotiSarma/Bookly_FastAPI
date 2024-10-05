from fastapi import APIRouter, status, HTTPException, Depends, dependencies
from src.books.schemas import Book, BookUpdate, BookCreate
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.books.service import BooksService
from src.auth.dependencies import AccessTokenBearer, RoleChecker

admin_checker = Depends(RoleChecker(["admin"]))
user_checker = Depends(RoleChecker(["user", "admin"]))

book_router = APIRouter()
book_service = BooksService()
access_token_bearer = AccessTokenBearer()



# Get All Books
@book_router.get("/books", dependencies=[admin_checker])
async def get_all_books(session:AsyncSession= Depends(get_session), token_data:dict = Depends(access_token_bearer)):
    all_books = await book_service.get_all_books(session)
    return all_books

# Get a Book
@book_router.get("/book/{book_uid}", dependencies=[user_checker])
async def get_single_book(book_uid: str, session:AsyncSession= Depends(get_session), token_data:dict = Depends(access_token_bearer)):
   book_detail = await book_service.get_single_book(book_uid, session)
   return book_detail
# Get User's All Books
@book_router.get("/user/all_books", dependencies=[user_checker])
async def get_user_books(session: AsyncSession = Depends(get_session), token_data: dict = Depends(access_token_bearer)):
    user_uid = token_data.get('user')['user_uid']

    user_books = await book_service.get_user_books(user_uid, session)
    return user_books

# Add Book
@book_router.post("/book/add_book", dependencies=[user_checker])
async def add_book(book_data: BookCreate, session:AsyncSession= Depends(get_session), token_data:dict = Depends(access_token_bearer)):
    user_uuid = token_data.get('user')['user_uid']
    return await book_service.create_book(book_data, user_uuid, session)
    

# Update Book
@book_router.patch("/book/update_book/{book_uid}", dependencies=[user_checker])
async def update_book(book_uid: str, book_update_data: BookUpdate, session:AsyncSession= Depends(get_session), token_data:dict = Depends(access_token_bearer)):
    update_book_detail = await book_service.update_book(book_uid, book_update_data,session)
    return update_book_detail
   

# Delete Book
@book_router.delete("/book/delete_book/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[user_checker])
async def delete_book(book_uid: str, session:AsyncSession= Depends(get_session), token_data:dict = Depends(access_token_bearer)):
    delete_book_detail = await book_service.delete_book(book_uid, session)
    return delete_book_detail