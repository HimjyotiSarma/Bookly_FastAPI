from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.requests import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.mail import create_message
from .schema import (
    UserCreateModal,
    UserResponseModal,
    UserLoginModal,
    UserBookModal,
    EmailModal,
)
from .service import UserService
from .utils import verify_pass, create_access_token
from datetime import timedelta, datetime
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.db.redis import add_jti_to_blacklist
from src.mail import create_message, mail
from src.config import settings
from .utils import create_safe_token, decode_safe_token
from fastapi.templating import Jinja2Templates
from pathlib import Path


# Register Jinja Template
BASE_DIR = Path(__file__).resolve().parent.parent
templates_folder = Path(BASE_DIR, "templates")
templates = Jinja2Templates(directory=f"{templates_folder}")


user_router = APIRouter()
user_service = UserService()


@user_router.get("/get_verify_mail_template", response_class=HTMLResponse)
async def get_verify_mail_template(
    request: Request,
    user_name: str,
    verification_url: str,
    current_year=datetime.today().year,
):
    return templates.TemplateResponse(
        request=request,
        name="email_verification_template.html",
        context={
            "user_name": user_name,
            "verification_url": verification_url,
            "current_year": current_year,
        },
    )


@user_router.post("/send_mail")
async def send_mail(emails: EmailModal):
    try:
        default_subject = "Authenticate your Email"
        default_body = "<h1>Welcome to the new Email Services</h1><br><h2>Authenticate by clicking your email below</h2>"
        message = create_message(
            recipients=emails.addresses,
            subject=emails.subject or default_subject,
            body=emails.body or default_body,
        )
        await mail.send_message(message)
        return JSONResponse(
            content={"message": "Email sent successfully"},
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@user_router.post(
    "/signup",
    response_model=UserResponseModal,
    response_model_exclude={"password_hash"},
)
async def create_user(
    user_data: UserCreateModal, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)
    if user_exists is True:
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED, detail="User Already Exists"
        )
    else:
        try:
            create_user_data = await user_service.create_user(user_data, session)

            safe_token = create_safe_token(data={"email": email})
            print("domain name: ", settings.DOMAIN)
            verification_email_link = f"http://{settings.DOMAIN}/{settings.ROOT_ROUTE}/{settings.VERSION}/auth/verify/{safe_token}"
            # html_message = await get_verify_mail_template(
            #     user_name=user_data.firstname, verification_url=verification_email_link
            # )
            html_message = templates.get_template(
                "email_verification_template.html"
            ).render(
                user_name=user_data.firstname,
                verification_url=verification_email_link,
                current_year=datetime.today().year,
            )
            print("HTML MESSAGE : -> ", html_message)
            email_response_model = EmailModal(
                addresses=[email], subject="Verify your Account", body=html_message
            )
            await send_mail(email_response_model)
            return create_user_data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Error getting User : {str(e)}",
            )


@user_router.post("/login")
async def log_User(
    user_data: UserLoginModal, session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    password = user_data.password

    user_Info = await user_service.get_user(email, session)

    if user_Info is not None:
        password_valid = verify_pass(password, user_Info.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    "email": user_Info.email,
                    "user_uid": str(user_Info.uid),
                    "role": user_Info.role,
                }
            )
            refresh_token = create_access_token(
                user_data={
                    "email": user_Info.email,
                    "user_uid": str(user_Info.uid),
                    "role": user_Info.role,
                },
                expiry=timedelta(days=7),
                refresh=True,
            )

            return JSONResponse(
                content={
                    "message": "User Logged in Successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "User": {
                        "email": user_Info.email,
                        "uid": str(user_Info.uid),
                        "role": user_Info.role,
                    },
                }
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid User Or Password"
    )


@user_router.get("/verify/{token}")
async def verify_account(token: str, session: AsyncSession = Depends(get_session)):
    token_details = decode_safe_token(token)
    if not token_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Safe Token Expired or Invalid. Please delete your account and try again",
        )
    user_email = token_details.get("email")
    user = await user_service.get_user(user_email, session)
    update_user = await user_service.update_user(user, {"is_verified": True}, session)
    return JSONResponse(
        content={
            "message": f"User with username {user.username} is Verified Successfully"
        },
        status_code=status.HTTP_200_OK,
    )


@user_router.get(
    "/me", response_model=UserBookModal, response_model_exclude={"password_hash"}
)
async def get_current_user(user=Depends(get_current_user)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Fetching Failed. Expired Token or Invalid Token",
        )
    return user


@user_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["expiry"]

    expiry_datetime = datetime.strptime(expiry_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    if expiry_datetime > datetime.now():
        access_token = create_access_token(user_data=token_details["user"])
        print(access_token)

        return JSONResponse(content={"access_token": access_token})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or Expired Token"
    )


@user_router.get("/logout")
async def revoke_token(token_data: dict = Depends(AccessTokenBearer())):
    jti = token_data["jti"]

    await add_jti_to_blacklist(jti)

    return JSONResponse(
        content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK
    )
