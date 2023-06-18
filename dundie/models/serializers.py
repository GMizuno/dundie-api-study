from datetime import datetime
from typing import Optional

from pydantic import BaseModel, root_validator
from sqlmodel import Session

from dundie.db import engine

from .user import User, generate_user
from ..security import get_password_hash


class TransactionResponse(BaseModel, extra="allow"):
    id: int
    value: int
    date: datetime

    # These 2 fields will be calculated at response time.
    user: Optional[str] = None
    from_user: Optional[str] = None

    @root_validator(pre=True)
    def get_usernames(cls, values: dict):
        with Session(engine) as session:
            user = session.get(User, values["user_id"])
            values["user"] = user and user.username # Guard clause, if user is not found use user instead.
            from_user = session.get(User, values["from_id"])
            values["from_user"] = from_user and from_user.username # Guard clause, if from_user is not found use from_user instead.
        return values


class UserResponse(BaseModel):
    """Serializer for when we send a response to the http client, like DTO"""

    name: str
    username: str
    dept: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    currency: str


class UserRequest(BaseModel):
    """Serializer for when we get the data from http client, like DTO"""

    name: str
    email: str
    dept: str
    password: str
    username: Optional[str] = None
    avatar: Optional[str]
    bio: Optional[str]
    currency: str = "USD"

    @root_validator(pre=True)
    def generate_username_if_not_set(cls, values):
        """Generate username if not set"""

        if values.get("username") is None:
            values["username"] = generate_user(values["name"])
        return values


class UserProfilePatchRequest(BaseModel):
    """Serializer for when cliente wants to partially update the user profile"""
    avatar: Optional[str]
    bio: Optional[str]

    @root_validator(pre=True)
    def ensure_values(cls, values):
        if not values:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided")
        return values


class UserPasswordPatchRequest(BaseModel):
    """Serializer for when cliente wants to update the user password"""
    password: str
    password_confirm: str

    @root_validator(pre=True)
    def check_password_match(cls, values):
        if values.get('password') != values.get('password_confirm'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        return values

    @property
    def hashed_password(self) -> str:
        """Returns hashed password"""
        return get_password_hash(self.password)
