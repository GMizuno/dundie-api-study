from typing import List
from sqlalchemy.orm import aliased
from fastapi import (
    APIRouter,
    HTTPException,
    Body,
    Depends
)
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, Session

from dundie.auth import (
    AuthenticatedUser,
    SuperUser,
    CanChangeUserPassword
)
from fastapi_pagination import (
    Page,
    Params
)
from fastapi_pagination.ext.sqlmodel import paginate

from dundie.db import ActiveSession
from dundie.models import (
    User,
    Balance,
)
from dundie.models.serializers import (
    UserResponse,
    UserRequest,
    UserProfilePatchRequest,
    UserPasswordPatchRequest,
    UserResponseWithBalance,
)
from dundie.tasks.user import try_to_send_pwd_reset_email
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import parse_obj_as
from dundie.auth import ShowBalanceField

router = APIRouter()

# TODO pagination
@router.get(
    "/",
    response_model=Page[UserResponse] | Page[UserResponseWithBalance],
)
async def list_user(
        *,
        session: Session = ActiveSession,
        params: Params = Depends(),
        show_balance_field: bool = ShowBalanceField,
):
    """List all users in the database."""
    if show_balance_field:
        query = select(User, Balance).join(Balance, User.id == Balance.user_id)
        return paginate(query=query, session=session, params=params)

    query = select(User)

    return paginate(query=query, session=session, params=params)


@router.post(
    "/",
    response_model=UserRequest,
    status_code=201,
    dependencies=[SuperUser]
)
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

@router.get(
    "/{username}/",
    response_model=UserResponse | UserResponseWithBalance,
    response_model_exclude_unset=True,
)
async def get_user_by_username(
        *, session: Session = ActiveSession, username: str, show_balance_field: bool = ShowBalanceField
):
    """Get user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if show_balance_field:
        user_with_balance = parse_obj_as(UserResponseWithBalance, user)
        return JSONResponse(jsonable_encoder(user_with_balance))
    return user

#TODO: Delete user
@router.post("/delete/{username}")
async def delete_user_by_username(*, session: Session = ActiveSession, username: str):
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