"""Adding final_grade and total_ratings to Movie table

Revision ID: 55fbe96430b8
Revises: 2ee9952e7b50
Create Date: 2024-09-15 21:09:27.688308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55fbe96430b8'
down_revision: Union[str, None] = '2ee9952e7b50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# "Add final_grade and total_ratings to Movie table"
def upgrade() -> None:
    op.add_column('movie', sa.Column('final_grade', sa.Float(), nullable=True))
    op.add_column('movie', sa.Column('total_ratings', sa.Integer(), nullable=True))

def downgrade() -> None:
    op.drop_column('movie', 'final_grade')
    op.drop_column('movie', 'total_ratings')