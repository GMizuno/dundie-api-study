"""ensure_admin_user

Revision ID: 0c832c6dac77
Revises: f45c1e4ce4d6
Create Date: 2023-06-17 20:39:26.924119

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from dundie.models.user import User  # NEW
from sqlmodel import Session  # NEW


# revision identifiers, used by Alembic.
revision = '0c832c6dac77'
down_revision = 'f45c1e4ce4d6'
branch_labels = None
depends_on = None


def upgrade() -> None:  # NEW
    bind = op.get_bind()
    session = Session(bind=bind)

    admin = User(
        name="Admin",
        username="admin",
        email="admin@dm.com",
        dept="management",
        currency="USD",
        password="admin",  # pyright: ignore
    )
    # if admin user already exists it will raise IntegrityError
    try:
        session.add(admin)
        session.commit()
    except sa.exc.IntegrityError:
        session.rollback()


def downgrade() -> None:
    pass