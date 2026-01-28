"""Add search fallback columns

Revision ID: 9b863d496e96
Revises: b838ef3372ca
Create Date: 2026-01-27 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b863d496e96'
down_revision = 'b838ef3372ca'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('reddit_object', sa.Column('use_search_fallback', sa.Boolean(), nullable=True))
    op.add_column('post', sa.Column('fetched_via_search', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('post', 'fetched_via_search')
    op.drop_column('reddit_object', 'use_search_fallback')
