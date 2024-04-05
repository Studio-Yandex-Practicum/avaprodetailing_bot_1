"""Add Car model

Revision ID: 4ba1aa7399d7
Revises: fcb5cd94bf6e
Create Date: 2024-04-05 16:31:32.433594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ba1aa7399d7'
down_revision: Union[str, None] = 'fcb5cd94bf6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('car',
    sa.Column('brand', sa.String(length=50), nullable=False),
    sa.Column('model', sa.String(length=50), nullable=False),
    sa.Column('number_plate', sa.String(length=9), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('number_plate')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('car')
    # ### end Alembic commands ###