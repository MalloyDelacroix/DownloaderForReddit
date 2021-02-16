"""add custom save paths

Revision ID: ab46745cf45e
Revises: 6dabad0d34fb
Create Date: 2021-02-16 09:38:49.686235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab46745cf45e'
down_revision = '6dabad0d34fb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('reddit_object', sa.Column('custom_post_save_path', sa.String(), nullable=True))
    op.add_column('reddit_object', sa.Column('custom_comment_save_path', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('reddit_object') as batch:
        batch.drop_column('custom_post_save_path')
        batch.drop_column('custom_comment_save_path')
