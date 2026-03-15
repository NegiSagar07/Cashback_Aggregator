"""add missing coupon columns for legacy schemas

Revision ID: 20260315_0002
Revises: 20260315_0001
Create Date: 2026-03-15 00:20:00
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20260315_0002"
down_revision: Union[str, None] = "20260315_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL-specific safety migration for existing tables created before discount_type/category.
    op.execute("ALTER TABLE coupons ADD COLUMN IF NOT EXISTS discount_type VARCHAR NOT NULL DEFAULT 'amount'")
    op.execute("ALTER TABLE coupons ADD COLUMN IF NOT EXISTS category VARCHAR NOT NULL DEFAULT 'Others'")


def downgrade() -> None:
    # Keep downgrade safe for environments where columns may not exist.
    op.execute("ALTER TABLE coupons DROP COLUMN IF EXISTS discount_type")
    op.execute("ALTER TABLE coupons DROP COLUMN IF EXISTS category")
