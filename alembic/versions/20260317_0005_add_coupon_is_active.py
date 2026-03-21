"""add is_active column to coupons

Revision ID: 20260317_0005
Revises: 20260317_0004
Create Date: 2026-03-17 00:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "20260317_0005"
down_revision: Union[str, None] = "20260317_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("coupons")}

    if "is_active" not in existing_columns:
        op.add_column(
            "coupons",
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("coupons")}

    if "is_active" in existing_columns:
        op.drop_column("coupons", "is_active")
