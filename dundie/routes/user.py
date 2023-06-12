from typing import List

from sqlmodel import select, Session

from dundie.db import ActiveSession
from dundie.models import User

from fastapi import APIRouter

from dundie.models.user import UserResponse

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def list_user(*, session: Session = ActiveSession):
    """List all users in the database."""
    users = session.exec(select(User)).all()
    return users
