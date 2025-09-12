"""change avg to Numeric(4,2) with computed

Revision ID: b36a98aabcad
Revises: c49befd06844
Create Date: 2025-09-12 20:41:49.486037

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b36a98aabcad'
down_revision: Union[str, Sequence[str], None] = 'c49befd06844'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('rating', 'avg')
    op.add_column(
        'rating',
        sa.Column(
            'avg',
            sa.Numeric(4, 2),
            sa.Computed(
                'ROUND((timeliness + completeness + quality) / 3.0, 2)',
                persisted=True,
            ),
        ),
    )


def downgrade() -> None:
    op.drop_column('rating', 'avg')
    op.add_column(
        'rating',
        sa.Column(
            'avg',
            sa.Float(),
            sa.Computed(
                '(timeliness + completeness + quality) / 3.0',
                persisted=True,
            ),
        ),
    )
