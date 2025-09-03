"""create licenses table

Revision ID: 0001
Revises: 
Create Date: 2025-09-03
"""

from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

license_type_enum = sa.Enum('free', 'pro', 'demo', name='licensetype')

def upgrade() -> None:
    bind = op.get_bind()
    license_type_enum.create(bind, checkfirst=True)
    op.create_table(
        'licenses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('license_type', license_type_enum, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('licenses')
    license_type_enum.drop(op.get_bind(), checkfirst=True)
