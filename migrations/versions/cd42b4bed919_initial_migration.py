"""Initial migration.

Revision ID: cd42b4bed919
Revises: 
Create Date: 2024-10-28 01:51:12.463545

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd42b4bed919'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('demand_prediction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('primary_category_alt', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('price_range_description', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('price', sa.Float(), nullable=False))
        batch_op.add_column(sa.Column('discount', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('description', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('upload_date_time', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('inventory_level', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('reorder_point', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('lead_time_days', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('supplier', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('last_restock_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('discount_percentage', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('total_revenue', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('demand', sa.Float(), nullable=False))
        batch_op.add_column(sa.Column('date', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('week', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('lag_1', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('rolling_mean', sa.Float(), nullable=True))
        batch_op.drop_column('prediction_date')
        batch_op.drop_column('predicted_demand')
        batch_op.drop_column('product_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('demand_prediction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_id', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('predicted_demand', sa.FLOAT(), nullable=False))
        batch_op.add_column(sa.Column('prediction_date', sa.DATETIME(), nullable=True))
        batch_op.drop_column('rolling_mean')
        batch_op.drop_column('lag_1')
        batch_op.drop_column('week')
        batch_op.drop_column('date')
        batch_op.drop_column('demand')
        batch_op.drop_column('total_revenue')
        batch_op.drop_column('discount_percentage')
        batch_op.drop_column('last_restock_date')
        batch_op.drop_column('supplier')
        batch_op.drop_column('lead_time_days')
        batch_op.drop_column('reorder_point')
        batch_op.drop_column('inventory_level')
        batch_op.drop_column('status')
        batch_op.drop_column('upload_date_time')
        batch_op.drop_column('description')
        batch_op.drop_column('discount')
        batch_op.drop_column('price')
        batch_op.drop_column('price_range_description')
        batch_op.drop_column('name')
        batch_op.drop_column('primary_category_alt')

    # ### end Alembic commands ###