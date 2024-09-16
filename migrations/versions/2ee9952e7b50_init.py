"""Init

Revision ID: 2ee9952e7b50
Revises: 
Create Date: 2024-09-15 18:06:04.681646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ee9952e7b50'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('admin_token', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('admin_token')
    )
    op.create_table(
        'movie',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('genre', sa.String(length=50), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('synopsis', sa.Text(), nullable=True),
        sa.Column('director', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'rental',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('movie_id', sa.Integer(), nullable=False),
        sa.Column('rental_date', sa.DateTime(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['movie_id'], ['movie.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('rental')
    op.drop_table('movie')
    op.drop_table('user')