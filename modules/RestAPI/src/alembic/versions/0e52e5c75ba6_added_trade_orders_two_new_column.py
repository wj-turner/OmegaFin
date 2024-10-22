"""Added trade_orders two new column

Revision ID: 0e52e5c75ba6
Revises: 0a6862dfcea1
Create Date: 2024-04-02 11:44:57.211464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e52e5c75ba6'
down_revision: Union[str, None] = '0a6862dfcea1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('trade_orders', sa.Column('commission', sa.Float(), nullable=True))
    op.add_column('trade_orders', sa.Column('fee', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('trade_orders', 'fee')
    op.drop_column('trade_orders', 'commission')
    # ### end Alembic commands ###
