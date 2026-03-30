from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status, Depends
from src.auth.utils import decode_token
from src.db.redis import is_jti_blocklisted
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from . service import UserService
from typing import List
from src.auth.models import User

user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials = await super().__call__(request)

        token = credentials.credentials

        token_data = decode_token(credentials.credentials)

        if not self.is_token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or has expired",
                    "resolution": "Please log in again to obtain a new token"
                },
            )
        
        print("--------------------------------------------------")
        print(token_data)
        print("--------------------------------------------------")

        if await is_jti_blocklisted(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token has been revoked",
                    "resolution": "Please log in again to obtain a new token"
                },
            )

        self.verify_token_data(token_data)

        return token_data
    
    def is_token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return True if token_data is not None else False
    
    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Subclasses must implement this method")

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access token cannot be a refresh token",
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token cannot be an access token",
            )
        
async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    user_email = token_details['user']['email']
    
    user = await user_service.get_user_by_email(email=user_email, session=session)
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role in self.allowed_roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action",
        )