"""
# --------------------------------------------------------------------------
# Authentication logic
# --------------------------------------------------------------------------
"""

import datetime as dt
from typing import Dict, Optional
from fastapi import HTTPException, Request, status, openapi, Depends
from fastapi.security import OAuth2, utils
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from jose import JWTError, jwt
from modules.settings import Settings
from modules.model import User
from modules.database import DataBase


class OAuth(OAuth2):
    """
    This class is taken directly from FastAPI:
    https://github.com/tiangolo/fastapi/blob/26f725d259c5dbe3654f221e608b14412c6b40da/fastapi/security/oauth2.py#L140-L171

    The only change made is that authentication is taken from a cookie
    instead of from the header!
    """

    def __init__(
        self,
        tokenUrl: str,
        settings: Settings,
        database: DataBase,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.settings = settings
        self.database = database
        if not scopes:
            scopes = {}

        flows = openapi.models.OAuthFlows(
            password={"tokenUrl": tokenUrl, "scopes": scopes}
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        # IMPORTANT: this is the line that differs from FastAPI. Here we use
        # `request.cookies.get(settings.COOKIE_NAME)` instead of
        # `request.headers.get("Authorization")`
        authorization = request.cookies.get(self.settings.COOKIE_NAME)

        scheme, param = utils.get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return param

    def get_current_user_from_token(self, token) -> User:
        """
        Get the current user from the cookies in a request.

        Use this function when you want to lock down a route so that only
        authenticated users can see access the route.
        """
        user = self.decode_token(token)
        return user

    def get_current_user_from_cookie(self, request: Request) -> User:
        """
        Get the current user from the cookies in a request.

        Use this function from inside other routes to get the current user. Good
        for views that should work for both logged in, and not logged in users.
        """
        token = str(request.cookies.get(self.settings.COOKIE_NAME))
        user = self.decode_token(token)
        return user

    def create_access_token(self, data: Dict, settings: Settings) -> str:
        to_encode = data.copy()
        expire = dt.datetime.utcnow() + dt.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def authenticate_user(self, email: str, plain_password: str):
        user = self.database.get_user(email)
        if not user:
            return False
        if not crypto.verify(plain_password, user.hashed_password):
            return False
        return user

    def decode_token(self, token) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )
        token = token.removeprefix("Bearer").strip()
        try:
            payload = jwt.decode(
                token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM]
            )
            email: str = payload.get("email")
            if email is None:
                raise credentials_exception
        except JWTError as e:
            print(e)
            raise credentials_exception from e

        user = self.database.get_user(email)
        return user
