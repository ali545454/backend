"""add google_id to user

Revision ID: 9d3f1e2a4b6c
Revises: 312274a03160
Create Date: 2026-03-14 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9d3f1e2a4b6c"
down_revision = "312274a03160"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("google_id", sa.String(length=255), nullable=True))
        batch_op.create_unique_constraint("uq_user_google_id", ["google_id"])


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_constraint("uq_user_google_id", type_="unique")
        batch_op.drop_column("google_id")
