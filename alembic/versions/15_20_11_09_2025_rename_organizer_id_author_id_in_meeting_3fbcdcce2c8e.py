"""rename organizer_id -> author_id in meeting"""

import sqlalchemy as sa

from alembic import op

revision = '3fbcdcce2c8e'
down_revision = '503e619925fa'


def upgrade() -> None:
    op.alter_column(
        'meeting',
        'organizer_id',
        new_column_name='author_id',
        existing_type=sa.Integer(),
    )


def downgrade() -> None:
    op.alter_column(
        'meeting',
        'author_id',
        new_column_name='organizer_id',
        existing_type=sa.Integer(),
    )
