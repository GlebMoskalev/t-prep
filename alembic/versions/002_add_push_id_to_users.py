"""Add push_id to users table

Revision ID: 002
Revises: 001
Create Date: 2024-12-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('push_id', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'push_id')
