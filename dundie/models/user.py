"""User related data models"""
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from dundie.security import HashedPassword, get_password_hash
from pydantic import BaseModel, root_validator
from fastapi import HTTPException, status

if TYPE_CHECKING:
    from dundie.models import Balance, Transaction

def generate_user(name: str) -> str:
    """Generates a slug from user.name"""
    "Gabriel Mizuno -> gabriel-mizuno"
    return name.lower().replace(" ", "-")

def generate_username(name: str) -> str:
    """Generates a slug username from a name"""
    return name.lower().replace(" ", "-")

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

    incomes: Optional[list["Transaction"]] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"primaryjoin": 'User.id == Transaction.user_id'},
    )
    # Populates a `.from_user` on `Transaction`
    expenses: Optional[list["Transaction"]] = Relationship(
        back_populates="from_user",
        sa_relationship_kwargs={"primaryjoin": 'User.id == Transaction.from_id'},
    )
    # Populates a `.user` on `Balance`
    _balance: Optional["Balance"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic"}
    )

    @property
    def balance(self) -> int:
        """Returns the current balance of the user"""
        if (user_balance := self._balance.first()) is not None:  # pyright: ignore
            return user_balance.value
        return 0

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