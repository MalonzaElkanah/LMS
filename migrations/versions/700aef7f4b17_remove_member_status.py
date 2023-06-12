"""remove member.status

Revision ID: 700aef7f4b17
Revises: ca33df0ba773
Create Date: 2023-06-09 22:25:51.686728

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "700aef7f4b17"
down_revision = "ca33df0ba773"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("member", schema=None) as batch_op:
        batch_op.drop_column("status")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("member", schema=None) as batch_op:
        batch_op.add_column(sa.Column("status", sa.VARCHAR(length=50), nullable=False))

    # ### end Alembic commands ###
