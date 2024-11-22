from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User
from sqlmodel import select, update, delete
from fastapi import HTTPException, status
from .schema import UserCreateModal
from .utils import generate_pass_hash
from fastapi.responses import JSONResponse


class UserService:
    async def get_user(self, email: str, session: AsyncSession):
        try:
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please provide Email Id",
                )

            statement = select(User).where(User.email == email)
            result = await session.exec(statement)

            user = result.first()

            return user

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error getting User : {str(e)}",
            )

    async def get_user_by_uid(self, uid: str, session: AsyncSession):
        try:
            if uid is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please provide correct User Id",
                )

            statement = select(User).where(User.uid == uid)
            result = await session.exec(statement)

            user = result.first()

            return user

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error getting User : {str(e)}",
            )

    async def user_exists(self, email: str, session: AsyncSession):
        try:
            user = await self.get_user(email, session)  # Fix: Await the get_user call
            return True if user is not None else False
        except HTTPException as e:
            # If a 404 is raised by get_user, this means the user does not exist.
            if e.status_code == status.HTTP_404_NOT_FOUND:
                return False
            raise e

    async def create_user(self, user_data: UserCreateModal, session: AsyncSession):
        try:
            user_data_dict = user_data.model_dump()  # Ensure you are using dict()

            if "role" in user_data_dict:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Manual Role Implementation is not Allowed",
                )

            new_user = User(**user_data_dict)

            new_user.role = "user"
            new_user.password_hash = generate_pass_hash(user_data_dict["password"])

            session.add(new_user)  # No need to await session.add()
            await session.commit()
            await session.refresh(new_user)

            return new_user

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating User : {str(e)}",
            )

    async def update_user(self, user: User, update_data: dict, session: AsyncSession):
        try:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                else:
                    raise ValueError(f"Invalid attribute: {key}")
            await session.commit()
            await session.refresh(user)
            return {
                "message": f"Account with username {user.username} updated successfully"
            }
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error Updating User : {str(e)}",
            )

    async def update_password(
        self, user: User, new_password: str, session: AsyncSession
    ):
        try:
            password_hash = generate_pass_hash(new_password)
            user.password_hash = password_hash
            await session.commit()
            await session.refresh(user)
            return JSONResponse(
                content={
                    "message": f"User with username {user.username}'s password has been updated successfully. Please Login to your account with the new password"
                },
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Something went wrong when updating password: {str(e)}",
            )
