from typing import List

from fastapi import APIRouter
from sqlmodel import select, Session

from dundie.db import ActiveSession
from dundie.models import User
from dundie.models.user import UserResponse, UserRequest
from dundie.auth import AuthenticatedUser, SuperUser

router = APIRouter()


@router.get("/", response_model=List[UserResponse], dependencies=[AuthenticatedUser])
async def list_user(*, session: Session = ActiveSession):
    """List all users in the database."""
    users = session.exec(select(User)).all()
    return users


@router.post("/", response_model=UserRequest, status_code=201, dependencies=[SuperUser])
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
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