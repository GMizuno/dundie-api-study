from datetime import timedelta, datetime
from functools import partial
from typing import Optional, Callable, Union

from fastapi import HTTPException, Request, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlmodel import select, Session

from dundie.config import settings
from dundie.db import engine
from dundie.models import User
from dundie.security import verify_password

ALGORITHM = settings.security.ALGORITHM
SECRET_KEY = settings.security.SECRET_KEY
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# Models

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None

# Logic

def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None,
        scope: str = 'access_token'
) -> str:
    """
    Creates a new access token for the user
    """
    to_enconde = data.copy()
    expires_delta = expires_delta or timedelta(minutes=15)
    expire = datetime.utcnow() + expires_delta
    to_enconde.update({'exp': expire, "scope": scope})
    encoded_jwt = jwt.encode(
        to_enconde,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

create_refresh_token = partial(create_access_token, scope="refresh_token")

def authenticate_user(
        get_user: Callable,
        username: str,
        password: str,
) -> Union[User, bool]:
    """
    Verifies if the user exist and password is correct
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_user(username: str) -> Optional[User]:
    """Get user by username"""

    with Session(engine) as session:
        return session.exec(
            select(User).where(User.username == username)
        ).first()


def get_current_user(
        token: str = Depends(oauth2_scheme),
        request: Request = None,  # pyright: ignore
        fresh=False
) -> User:
    """Get current user authenticated"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if request:
        if authorization := request.headers.get("authorization"):
            try:
                token = authorization.split(" ")[1]
            except IndexError:
                raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    if fresh and (not payload["fresh"]   and not user.superuser):
        raise credentials_exception

    return user

# FastAPI dependencies


async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """Wraps the sync get_active_user for sync calls"""
    return current_user


AuthenticatedUser = Depends(get_current_active_user)


async def validate_token(token: str = Depends(oauth2_scheme)) -> User:
    """Validates user token"""
    user = get_current_user(token=token)
    return user
