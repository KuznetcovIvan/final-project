"""add start_at and due_at to task

Revision ID: fff24644d3e9
Revises: b6a14d852177
Create Date: 2025-09-09 17:47:44.592288

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fff24644d3e9'
down_revision: Union[str, Sequence[str], None] = 'b6a14d852177'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('task', sa.Column('start_at', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('due_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('task', 'due_at')
    op.drop_column('task', 'start_at')
