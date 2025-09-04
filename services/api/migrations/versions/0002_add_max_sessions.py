"""add max_sessions column to user

Revision ID: 0002
Revises: 0001
Create Date: 2025-09-03
"""

from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('user', sa.Column('max_sessions', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    op.drop_column('user', 'max_sessions')
