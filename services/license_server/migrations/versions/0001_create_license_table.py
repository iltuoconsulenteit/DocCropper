from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    license_type_enum = sa.Enum('free', 'demo', 'demo_full', 'developer', 'pro', name='licensetype')
    license_type_enum.create(op.get_bind())
    op.create_table(
        'licenses',
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('license_type', sa.Enum('free', 'demo', 'demo_full', 'developer', 'pro', name='licensetype'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('allowed_domains', postgresql.ARRAY(sa.String())),
        sa.Column('plugins', postgresql.JSON()),
        sa.Column('settings', postgresql.JSON()),
        sa.PrimaryKeyConstraint('key')
    )


def downgrade():
    op.drop_table('licenses')
    sa.Enum(name='licensetype').drop(op.get_bind())
