"""create posts table

Revision ID: 5ed6f96f51be
Revises: 
Create Date: 2023-11-28 12:58:45.139955

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ed6f96f51be'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable=False,
                    primary_key=True), sa.Column('title', sa.String(), nullable=False))    
    pass


def downgrade() -> None:
    op.drop_table('posts')
    pass
