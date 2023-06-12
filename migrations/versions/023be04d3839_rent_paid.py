"""rent_paid

Revision ID: 023be04d3839
Revises: 700aef7f4b17
Create Date: 2023-06-11 16:02:42.846479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "023be04d3839"
down_revision = "700aef7f4b17"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("transaction", schema=None) as batch_op:
        batch_op.add_column(sa.Column("rent_paid", sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("transaction", schema=None) as batch_op:
        batch_op.drop_column("rent_paid")

    # ### end Alembic commands ###
