"""empty message

Revision ID: 6dabad0d34fb
Revises: 70d9de393850
Create Date: 2020-10-12 12:25:53.840119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6dabad0d34fb'
down_revision = '70d9de393850'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('reddit_object_list', sa.Column('update_date_limit', sa.Boolean(), nullable=False,
                                                  server_default='1'))


def downgrade():
    with op.batch_alter_table('reddit_object_list') as batch:
        batch.drop_column('update_date_limit')
