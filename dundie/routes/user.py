from typing import List

from fastapi import APIRouter, HTTPException, Body
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, Session

from dundie.auth import (
    AuthenticatedUser,
    SuperUser,
    CanChangeUserPassword
)
from dundie.db import ActiveSession
from dundie.models import User
from dundie.models.user import (
    UserResponse,
    UserRequest,
    UserProfilePatchRequest,
    UserPasswordPatchRequest
)
from dundie.tasks.user import try_to_send_pwd_reset_email

router = APIRouter()


@router.get("/", response_model=List[UserResponse], dependencies=[AuthenticatedUser])
async def list_user(*, session: Session = ActiveSession):
    """List all users in the database."""
    users = session.exec(select(User)).all()
    return users


@router.post("/", response_model=UserRequest, status_code=201, dependencies=[SuperUser])
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    # Podeira usar um if para verificar se o usuário e email já existem
    db_user = User.from_orm(user)
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=500,
            detail="User already exists"
        )
    session.refresh(db_user) # Retorna o objeto atualizado para db_user
    return db_user

@router.get("/{username}", response_model=UserResponse)
async def get_user_by_username(*, session: Session = ActiveSession, username: str):
    """Get user by username"""
    user = session.exec(select(User).where(User.username == username)).first()
    return user

#TODO: Delete user
@router.post("/delete/{username}")
async def get_user_by_username(*, session: Session = ActiveSession, username: str):
    """Delete user by username"""
    pass

@router.patch("/{username}/", response_model=UserResponse)
async def update_user(
        *,
        session: Session = ActiveSession,
        patch_data: UserProfilePatchRequest,
        current_user: User = AuthenticatedUser,
        username: str
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    user.avatar = patch_data.avatar
    user.bio = patch_data.bio

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/{username}/password/", response_model=UserResponse)
async def change_password(
        *,
        session: Session = ActiveSession,
        patch_data: UserPasswordPatchRequest,
        user: User = CanChangeUserPassword
):
    user.password = patch_data.hashed_password  # pyright: ignore
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/pwd_reset_token/")
async def send_password_reset_token(*, email: str = Body(embed=True)): # Body is generic serializer
    """Sends an email with the token to reset password."""
    try_to_send_pwd_reset_email(email)
    return {
        "message": "If we found a user with that email, we sent a password reset token to it."
    }