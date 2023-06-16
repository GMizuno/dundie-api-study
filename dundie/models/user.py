"""User related data models"""
from typing import Optional
from sqlmodel import Field, SQLModel
from dundie.security import HashedPassword
from pydantic import BaseModel, root_validator


class User(SQLModel, table=True):
    """Represents the User Model, can connect to the database using ORM"""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: HashedPassword
    name: str = Field(nullable=False)
    dept: str = Field(nullable=False)
    currency: str = Field(nullable=False)

    @property
    def superuser(self):
        """Users belonging to management dept are admins."""
        return self.dept == "management"

def generate_user(name: str) -> str:
    """Generates a slug from user.name"""
    "Gabriel Mizuno -> gabriel-mizuno"
    return name.lower().replace(" ", "-")

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


def generate_username(name: str) -> str:
    """Generates a slug username from a name"""
    return name.lower().replace(" ", "-")