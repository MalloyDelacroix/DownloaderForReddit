"""empty message

Revision ID: 0a5e43b49d6a
Revises: c19eae85081c
Create Date: 2020-06-10 11:06:48.852454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a5e43b49d6a'
down_revision = 'c19eae85081c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('retry_attempts', sa.Integer(), nullable=True))
    op.add_column('content', sa.Column('retry_attempts', sa.Integer(), nullable=True))
    op.add_column('post', sa.Column('retry_attempts', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'retry_attempts')
    op.drop_column('content', 'retry_attempts')
    op.drop_column('comment', 'retry_attempts')
    # ### end Alembic commands ###