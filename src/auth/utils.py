from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid
from src.config import settings
import jwt
import logging


password_context = CryptContext(
    schemes=['bcrypt']
)

def generate_pass_hash(password: str)-> str:
    hash = password_context.hash(password)
    return hash
def verify_pass(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
        expiry_datetime = datetime.now() + (expiry if expiry is not None else timedelta(minutes=60))
        payload ={
            'jti': str(uuid.uuid4()),
            'user': user_data,
            'expiry': expiry_datetime.isoformat(),
            'refresh': refresh
        }
        token_id = jwt.encode(
            payload=payload,
            key = settings.JWT_PRIVATE,
            algorithm=settings.JWT_ALGORITHM
        )
        return token_id

def decode_token(token: str):
    try:
        token_data = jwt.decode(
            jwt=token,
            key= settings.JWT_PRIVATE,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None
    except Exception as e:
        logging.exception(e)
        return None

    