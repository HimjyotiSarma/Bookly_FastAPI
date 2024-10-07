from typing import Optional, Dict, List
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import decode_token
from src.db.redis import token_in_blacklist
from src.db.main import get_session
from src.auth.service import UserService
from src.db.models import User


user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[Dict]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        token_data = decode_token(credentials.credentials)

        if not self.token_valid(credentials.credentials):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get a new token"
                }
            )
        if(await token_in_blacklist(token_data['jti'])):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get a new token"
                }
            )
        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:
        return decode_token(token) is not None

    def verify_token_data(self, token_data: dict):
        """This should be overridden in subclasses for custom validation."""
        raise NotImplementedError("Please override 'verify_token_data' in child classes")

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and  not token_data.get('refresh'):
            return token_data
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please provide an Access Token"
        )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data.get('refresh'):
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please provide a Refresh Token"
        )
    
async def get_current_user(token_details: dict= Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    user_email = token_details['user']['email']

    user_detail = await user_service.get_user(user_email, session)

    return user_detail

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role in self.allowed_roles:
            return True
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")


