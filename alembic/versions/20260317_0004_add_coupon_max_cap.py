"""add max_cap column to coupons

Revision ID: 20260317_0004
Revises: 20260316_0003
Create Date: 2026-03-17 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "20260317_0004"
down_revision: Union[str, None] = "20260316_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("coupons")}

    if "max_cap" not in existing_columns:
        op.add_column("coupons", sa.Column("max_cap", sa.Float(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("coupons")}

    if "max_cap" in existing_columns:
        op.drop_column("coupons", "max_cap")
