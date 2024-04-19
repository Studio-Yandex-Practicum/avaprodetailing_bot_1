"""First migration

Revision ID: a5baa1753ab2
Revises: 
Create Date: 2024-04-18 11:54:07.482081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5baa1753ab2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('loyalitysettings',
    sa.Column('default_value', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(length=16), nullable=True),
    sa.Column('telegram_id', sa.String(length=32), nullable=True),
    sa.Column('first_name', sa.String(length=32), nullable=True),
    sa.Column('second_name', sa.String(length=32), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_number'),
    sa.UniqueConstraint('telegram_id')
    )
    op.create_table('car',
    sa.Column('brand', sa.String(length=50), nullable=False),
    sa.Column('model', sa.String(length=50), nullable=False),
    sa.Column('number_plate', sa.String(length=9), nullable=False),
    sa.Column('owner_telegram_id', sa.String(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_telegram_id'], ['user.telegram_id'], name='fk_car_owner_telegram_id_user', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('number_plate')
    )
    op.create_table('loyalitysettingshistory',
    sa.Column('changed_by_id', sa.Integer(), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('old_data', sa.String(length=255), nullable=False),
    sa.Column('new_data', sa.String(length=255), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['changed_by_id'], ['user.id'], name='fk_loyalitysettingshistory_changed_by_id_user'),
    sa.ForeignKeyConstraint(['object_id'], ['loyalitysettings.id'], name='fk_loyalitysettingshistory_object_id_loyalitysettings'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment',
    sa.Column('generated_payment_id', sa.String(length=36), nullable=True),
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
    op.create_table('userhistory',
    sa.Column('changed_by_id', sa.Integer(), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('old_data', sa.String(length=255), nullable=False),
    sa.Column('new_data', sa.String(length=255), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['changed_by_id'], ['user.id'], name='fk_userhistory_changed_by_id_user'),
    sa.ForeignKeyConstraint(['object_id'], ['user.id'], name='fk_userhistory_object_id_user'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('carhistory',
    sa.Column('changed_by_id', sa.Integer(), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('old_data', sa.String(length=255), nullable=False),
    sa.Column('new_data', sa.String(length=255), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['changed_by_id'], ['user.id'], name='fk_carhistory_changed_by_id_user', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['object_id'], ['car.id'], name='fk_carhistory_car_id_car', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('loyality',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('payment_id', sa.Integer(), nullable=True),
    sa.Column('action', sa.Enum('charge', 'write_off', name='loyalityaction'), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('edited', sa.Boolean(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('exp_date', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['payment_id'], ['payment.id'], name='fk_loyality_payment_id_payment'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_loyality_user_id_user'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('loyalityhistory',
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('new_data', sa.String(length=255), nullable=False),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('loyality_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['user.id'], name='fk_loyalityhistory_admin_id_user'),
    sa.ForeignKeyConstraint(['loyality_id'], ['loyality.id'], name='fk_loyalityhistory_loyality_id_loyality'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_loyalityhistory_user_id_user'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('loyalityhistory')
    op.drop_table('loyality')
    op.drop_table('carhistory')
    op.drop_table('userhistory')
    op.drop_table('payment')
    op.drop_table('loyalitysettingshistory')
    op.drop_table('car')
    op.drop_table('user')
    op.drop_table('loyalitysettings')
    # ### end Alembic commands ###
