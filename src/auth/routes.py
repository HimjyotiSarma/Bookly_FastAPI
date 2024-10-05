from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .schema import UserCreateModal, UserResponseModal, UserLoginModal, UserBookModal
from .service import UserService
from .utils import verify_pass, create_access_token
from datetime import timedelta, datetime
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blacklist


user_router = APIRouter()
user_service = UserService()



@user_router.post("/signup", response_model=UserResponseModal, response_model_exclude={'password_hash'})
async def create_user(user_data: UserCreateModal,session: AsyncSession = Depends(get_session)):
    email = user_data.email
    
    user_exists = await user_service.user_exists(email, session)
    if(user_exists is True):
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail="User Already Exists")
    else:
        try:
            create_user_data = await user_service.create_user(user_data,session)
            return create_user_data
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Error getting User : {str(e)}")

@user_router.post("/login")
async def log_User(user_data: UserLoginModal, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    password = user_data.password

    user_Info= await user_service.get_user(email, session)

    if(user_Info is not None):
        password_valid = verify_pass(password, user_Info.password_hash)

        if(password_valid):
            access_token = create_access_token(
                user_data= {
                    'email': user_Info.email,
                    'user_uid': str(user_Info.uid),
                    'role': user_Info.role
                }
            )
            refresh_token = create_access_token(
                user_data={
                    'email': user_Info.email,
                    'user_uid': str(user_Info.uid),
                    'role': user_Info.role
                },
                expiry=timedelta(days=7),
                refresh=True
            )

            return JSONResponse(
                content={
                    "message": "User Logged in Successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "User":{
                        "email": user_Info.email,
                        "uid": str(user_Info.uid),
                        'role': user_Info.role
                    }
                }
            )
        
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid User Or Password")

@user_router.get("/me", response_model=UserBookModal, response_model_exclude={'password_hash'})
async def get_current_user(user = Depends(get_current_user)):
    if(user is None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Fetching Failed. Expired Token or Invalid Token")
    return user

@user_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["expiry"]

    expiry_datetime = datetime.strptime(expiry_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    if expiry_datetime > datetime.now():
        access_token = create_access_token(user_data=token_details['user'])
        print(access_token)

        return JSONResponse(content={"access_token": access_token})
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or Expired Token")

@user_router.get('/logout')
async def revoke_token(token_data: dict = Depends(AccessTokenBearer())):
    jti = token_data['jti']

    await add_jti_to_blacklist(jti)

    return JSONResponse(
        content={
            "message": "Logged Out Successfully"
        },
        status_code=status.HTTP_200_OK
    )
    
    