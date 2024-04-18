"""Add Payment model and relationship in User model.

Revision ID: d1e311cc96d4
Revises: 0a17ab2ba466
Create Date: 2024-04-12 22:39:56.452320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e311cc96d4'
down_revision: Union[str, None] = '0a17ab2ba466'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment',
    sa.Column('generated_payment_id', sa.String(length=36), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('payment_method', sa.Enum('online', 'cash', name='paymentmethod'), nullable=False),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('payer_id', sa.Integer(), nullable=True),
    sa.Column('is_paid', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['user.id'], name='fk_payment_admin_id_user'),
    sa.ForeignKeyConstraint(['payer_id'], ['user.id'], name='fk_payment_payer_id_user'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('generated_payment_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment')
    # ### end Alembic commands ###
