from .schemas import TagModal, TagCreateModal, TagAddModal
from src.db.models import Tag
from src.books.service import BooksService
from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlmodel import select, desc, delete
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

book_service = BooksService()


class TagService:
    async def get_all_tags(self, session: AsyncSession):
        try:
            # Fetch all tags ordered by creation date descending
            statement = select(Tag).order_by(desc(Tag.created_at))
            result = await session.exec(statement)
            return result.all()

        except Exception as e:
            # Rollback transaction on error and raise HTTPException
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error getting Tag List: {str(e)}",
            )

    async def get_single_tag(self, tag_name: str, session: AsyncSession):
        try:
            statement = select(Tag).where(Tag.name == tag_name)
            result = await session.exec(statement)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No Tag with the Tag name {str(tag_name)} found inb the Database",
                )
            return result.first()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error getting Tag: {str(e)}",
            )

    async def add_tag_to_book(
        self, tag_list: TagAddModal, book_uid: str, session: AsyncSession
    ):
        try:
            book = await book_service.get_single_book(book_uid, session)
            print("<----BOOK INFO---->", book)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Book with UID {book_uid} not found.",
                )

            for tag_info in tag_list.tags:
                statement = select(Tag).where(Tag.name == tag_info.name)
                result = await session.exec(statement)
                tag_data = result.one_or_none()
                if not tag_data:
                    tag_data = Tag(name=tag_info.name)
                    session.add(tag_data)
                book.tags.append(tag_data)

            session.add(book)
            await session.commit()
            await session.refresh(book)
            return book

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error getting Tag List: {str(e)}",
            )

    async def get_tag_by_uid(self, tag_id: str, session: AsyncSession):
        try:
            statement = select(Tag).where(Tag.uid == tag_id)
            result = await session.exec(statement)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tag not found in Database.",
                )
            return result.first()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error getting Tag : {str(e)}",
            )

    async def add_tag(self, tag_data: TagCreateModal, session: AsyncSession):
        try:
            # Check if the tag already exists
            existing_tag = await self.get_single_tag(tag_data.name, session)
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Tag with name {tag_data.name} already exists.",
                )

            # Create and add a new tag if not existing
            new_tag = Tag(name=tag_data.name)
            session.add(new_tag)
            await session.commit()
            await session.refresh(new_tag)
            return new_tag

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Error creating tag: {e}",
            )

    async def update_tag(
        self, tag_id: str, tag_update_info: TagCreateModal, session: AsyncSession
    ):
        try:
            tag_info = await self.get_tag_by_uid(tag_id, session)
            tag_update_dict = tag_update_info.model_dump()
            for key, value in tag_update_dict.items():
                setattr(tag_info, key, value)
            await session.commit()
            await session.refresh(tag_info)
            return tag_info
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Error Updating Tag : {str(e)}",
            )

    async def delete_tag(self, tag_id: str, session: AsyncSession):
        try:
            tag_info = await self.get_tag_by_uid(tag_id, session)
            await session.delete(tag_info)
            await session.commit()
            return JSONResponse(
                content={"message": f"Tag '{tag_info.name}' deleted successfully"},
                status_code=status.HTTP_202_ACCEPTED,
                media_type="application/json",
            )

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Error Deleting Tag : {str(e)}",
            )
