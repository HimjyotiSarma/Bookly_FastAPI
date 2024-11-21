from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid
from src.config import settings
import jwt
import logging
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from src.config import settings

password_context = CryptContext(schemes=["bcrypt"])


def generate_pass_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash


def verify_pass(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    expiry_datetime = datetime.now() + (
        expiry if expiry is not None else timedelta(minutes=60)
    )
    payload = {
        "jti": str(uuid.uuid4()),
        "user": user_data,
        "expiry": expiry_datetime.isoformat(),
        "refresh": refresh,
    }
    token_id = jwt.encode(
        payload=payload, key=settings.JWT_PRIVATE, algorithm=settings.JWT_ALGORITHM
    )
    return token_id


def decode_token(token: str):
    try:
        token_data = jwt.decode(
            jwt=token, key=settings.JWT_PRIVATE, algorithms=[settings.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None
    except Exception as e:
        logging.exception(e)
        return None


def create_safe_token(data: dict):
    try:
        serializer = URLSafeTimedSerializer(secret_key=settings.DANGEROUS_TOKEN)
        token = serializer.dumps(data, salt="email_verification")
        return token
    except Exception as e:
        logging.error(f"Error Creating Dangerous Token : {str(e)}")
        return None


def decode_safe_token(token: str):
    try:
        serializer = URLSafeTimedSerializer(secret_key=settings.DANGEROUS_TOKEN)
        token_data = serializer.loads(
            token, max_age=settings.DANGEROUS_MAX_AGE, salt="email_verification"
        )
        return token_data
    except SignatureExpired as e:
        logging.error(f"Dangerous Token Expired : {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error Decoding Safe Token : {str(e)}")
        return None
