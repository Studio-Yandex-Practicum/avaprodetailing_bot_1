"""empty message

Revision ID: bf25ac8010fc
Revises: 4ba1aa7399d7, ed3cf9a6c957
Create Date: 2024-04-06 23:58:09.075929

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf25ac8010fc'
down_revision: Union[str, None] = ('4ba1aa7399d7', 'ed3cf9a6c957')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
