"""migrate

Revision ID: 5c6dff3be701
Revises: b0ab23c6b955
Create Date: 2021-02-24 16:04:32.846106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c6dff3be701'
down_revision = 'b0ab23c6b955'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('content', sa.String(length=600), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_author'), 'comments', ['author'], unique=False)
    op.create_index(op.f('ix_comments_content'), 'comments', ['content'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_comments_content'), table_name='comments')
    op.drop_index(op.f('ix_comments_author'), table_name='comments')
    op.drop_table('comments')
    # ### end Alembic commands ###
