from datetime import timedelta, datetime
from typing import Optional, Callable, Union

from fastapi import HTTPException, Request, status
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
oath2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# Models

class Token(BaseModel):
    acess_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None


def create_acess_token(
        data: dict,
        expires_delta: Optional[timedelta] = None,
        scope: str = 'acess_token'
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


def autheticante_user(
        get_user: Callable,
        username: str,
        password: str,
) -> Union[User, bool]:
    """
    Verifies if the user exist and password is corret
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


def get_current_user(token: str) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})
        token_data = TokenData(username=username) # Serialize the data, could diferent
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})
    user = get_user(username=token_data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})
    return user


async def validate_token(token: str) -> User:
    user = get_current_user(token=token)
    return user
