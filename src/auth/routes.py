from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from .schemas import UserCreateModel, UserModel, UserLoginModel, UserBooksModel
from .service import UserService
from src.db.main import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from datetime import timedelta
from . utils import create_access_token, decode_token, verify_password
from . dependencies import RefreshTokenBearer, AccessTokenBearer, RoleChecker, get_current_user
from datetime import datetime
from src.db.redis import add_jti_to_blacklist

REFRESH_TOKEN_EXPIRY = timedelta(days=7)

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

@auth_router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UserModel)
async def signup(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email

    user_exists = await user_service.user_exists(email=email, session=session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    new_user = await user_service.create_user(user_data=user_data, session=session)

    return new_user

@auth_router.post('/login')
async def login(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email    
    password = login_data.password

    user = await user_service.get_user_by_email(email=email, session=session) 

    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                }
            )

            refresh_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                },
                expiry=REFRESH_TOKEN_EXPIRY,
                refresh=True,
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid),
                    }
                }
            )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password"
    )

@auth_router.post('/refresh-token')
async def refresh_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_details['user']
        )

        return JSONResponse(
            content={
                "access_token": new_access_token,
            }
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token has expired, please log in again"
    )

@auth_router.get('/me', response_model=UserBooksModel)
async def get_current_user(user = Depends(get_current_user), _: bool = Depends(role_checker)):
    return user


@auth_router.get('/logout')
async def logout(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details['jti']
    await add_jti_to_blacklist(jti)
    return JSONResponse(
        content={
            "message": "Logout successful"
        }
    )