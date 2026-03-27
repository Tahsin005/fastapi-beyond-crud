from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import UserCreateModel, UserModel
from .service import UserService
from src.db.main import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession

auth_router = APIRouter()
user_service = UserService()

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

