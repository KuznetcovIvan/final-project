"""add check constraints to rating

Revision ID: 77e61666f7a2
Revises: b36a98aabcad
Create Date: 2025-09-12 21:56:10.591533

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '77e61666f7a2'
down_revision: Union[str, Sequence[str], None] = 'b36a98aabcad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'rating',
        'avg',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        type_=sa.Float(),
        existing_nullable=True,
    )
    op.create_check_constraint(
        'timeliness_1-5',
        'rating',
        'timeliness BETWEEN 1 AND 5',
    )
    op.create_check_constraint(
        'completeness_1-5',
        'rating',
        'completeness BETWEEN 1 AND 5',
    )
    op.create_check_constraint(
        'quality_1-5',
        'rating',
        'quality BETWEEN 1 AND 5',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('timeliness_1-5', 'rating', type_='check')
    op.drop_constraint('completeness_1-5', 'rating', type_='check')
    op.drop_constraint('quality_1-5', 'rating', type_='check')
    op.alter_column(
        'rating',
        'avg',
        existing_type=sa.Float(),
        type_=sa.NUMERIC(precision=4, scale=2),
        existing_nullable=True,
    )
