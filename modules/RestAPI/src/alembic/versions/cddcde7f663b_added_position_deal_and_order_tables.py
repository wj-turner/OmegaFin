"""Added position, deal and order tables

Revision ID: cddcde7f663b
Revises: 0e52e5c75ba6
Create Date: 2024-04-04 12:33:51.126131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cddcde7f663b'
down_revision: Union[str, None] = '0e52e5c75ba6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('deals',
    sa.Column('ticket', sa.BigInteger(), nullable=False),
    sa.Column('order', sa.BigInteger(), nullable=True),
    sa.Column('time', sa.BigInteger(), nullable=True),
    sa.Column('time_msc', sa.BigInteger(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('entry', sa.Integer(), nullable=True),
    sa.Column('magic', sa.BigInteger(), nullable=True),
    sa.Column('position_id', sa.BigInteger(), nullable=True),
    sa.Column('reason', sa.Integer(), nullable=True),
    sa.Column('volume', sa.Float(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('commission', sa.Float(), nullable=True),
    sa.Column('swap', sa.Float(), nullable=True),
    sa.Column('profit', sa.Float(), nullable=True),
    sa.Column('fee', sa.Float(), nullable=True),
    sa.Column('symbol', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('external_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('ticket')
    )
    op.create_table('orders',
    sa.Column('ticket', sa.BigInteger(), nullable=False),
    sa.Column('time_setup', sa.BigInteger(), nullable=True),
    sa.Column('time_setup_msc', sa.BigInteger(), nullable=True),
    sa.Column('time_done', sa.BigInteger(), nullable=True),
    sa.Column('time_done_msc', sa.BigInteger(), nullable=True),
    sa.Column('time_expiration', sa.BigInteger(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('type_time', sa.Integer(), nullable=True),
    sa.Column('type_filling', sa.Integer(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.Column('magic', sa.BigInteger(), nullable=True),
    sa.Column('position_id', sa.BigInteger(), nullable=True),
    sa.Column('position_by_id', sa.BigInteger(), nullable=True),
    sa.Column('reason', sa.Integer(), nullable=True),
    sa.Column('volume_initial', sa.Float(), nullable=True),
    sa.Column('volume_current', sa.Float(), nullable=True),
    sa.Column('price_open', sa.Float(), nullable=True),
    sa.Column('sl', sa.Float(), nullable=True),
    sa.Column('tp', sa.Float(), nullable=True),
    sa.Column('price_current', sa.Float(), nullable=True),
    sa.Column('price_stoplimit', sa.Float(), nullable=True),
    sa.Column('symbol', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('external_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('ticket')
    )
    op.create_table('positions',
    sa.Column('ticket', sa.BigInteger(), nullable=False),
    sa.Column('time', sa.BigInteger(), nullable=True),
    sa.Column('time_msc', sa.BigInteger(), nullable=True),
    sa.Column('time_update', sa.BigInteger(), nullable=True),
    sa.Column('time_update_msc', sa.BigInteger(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('magic', sa.BigInteger(), nullable=True),
    sa.Column('identifier', sa.BigInteger(), nullable=True),
    sa.Column('reason', sa.Integer(), nullable=True),
    sa.Column('volume', sa.Float(), nullable=True),
    sa.Column('price_open', sa.Float(), nullable=True),
    sa.Column('sl', sa.Float(), nullable=True),
    sa.Column('tp', sa.Float(), nullable=True),
    sa.Column('price_current', sa.Float(), nullable=True),
    sa.Column('swap', sa.Float(), nullable=True),
    sa.Column('profit', sa.Float(), nullable=True),
    sa.Column('symbol', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('external_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('ticket')
    )
    op.drop_table('trade_orders')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('trade_orders',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('ticket', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('symbol', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('price_open', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('price_current', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('volume_initial', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('volume_current', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('time_setup', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('time_done', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('state', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('type', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('position_status', postgresql.ENUM('open', 'closed', name='position_status_enum'), autoincrement=False, nullable=False),
    sa.Column('sl', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('tp', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('swap', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('profit', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('reason', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('magic', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('comment', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('external_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('commission', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('fee', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='trade_orders_pkey'),
    sa.UniqueConstraint('ticket', name='trade_orders_ticket_key')
    )
    op.drop_table('positions')
    op.drop_table('orders')
    op.drop_table('deals')
    # ### end Alembic commands ###