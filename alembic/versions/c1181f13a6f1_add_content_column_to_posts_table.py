"""add content column to posts table

Revision ID: c1181f13a6f1
Revises: 5ed6f96f51be
Create Date: 2023-11-28 14:45:32.778982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1181f13a6f1'
down_revision: Union[str, None] = '5ed6f96f51be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
