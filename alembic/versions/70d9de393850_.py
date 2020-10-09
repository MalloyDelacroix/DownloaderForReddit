"""empty message

Revision ID: 70d9de393850
Revises: 
Create Date: 2020-10-08 07:35:57.791315

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70d9de393850'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('reddit_object', sa.Column('update_date_limit', sa.Boolean(), nullable=False, server_default='1'))


def downgrade():
    with op.batch_alter_table('reddit_object') as batch:
        batch.drop_column('update_date_limit')
