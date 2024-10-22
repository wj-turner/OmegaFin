"""Add unique constraint to login in user_profiles

Revision ID: 31d35ae87c58
Revises: 68261d929a86
Create Date: 2024-04-18 11:37:20.738314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31d35ae87c58'
down_revision: Union[str, None] = '68261d929a86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'user_profiles', ['login'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_profiles', type_='unique')
    # ### end Alembic commands ###
