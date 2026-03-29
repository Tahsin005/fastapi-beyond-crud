from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status
from src.auth.utils import decode_token
from src.db.redis import is_jti_blocklisted, add_jti_to_blacklist

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