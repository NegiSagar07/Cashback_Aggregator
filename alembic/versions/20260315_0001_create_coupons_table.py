"""create coupons table

Revision ID: 20260315_0001
Revises: 
Create Date: 2026-03-15 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "20260315_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("coupons"):
        op.create_table(
            "coupons",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("platform", sa.String(), nullable=False),
            sa.Column("discount_type", sa.String(), nullable=False, server_default="amount"),
            sa.Column("value", sa.Float(), nullable=False),
            sa.Column("min_spend", sa.Float(), nullable=True),
            sa.Column("expiry", sa.Date(), nullable=False),
            sa.Column("category", sa.String(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        existing_columns = {col["name"] for col in inspector.get_columns("coupons")}

        if "discount_type" not in existing_columns:
            op.add_column(
                "coupons",
                sa.Column(
                    "discount_type",
                    sa.String(),
                    nullable=False,
                    server_default="amount",
                ),
            )

        if "category" not in existing_columns:
            op.add_column(
                "coupons",
                sa.Column(
                    "category",
                    sa.String(),
                    nullable=False,
                    server_default="Others",
                ),
            )

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("coupons")}
    coupon_id_index = op.f("ix_coupons_id")
    if coupon_id_index not in existing_indexes:
        op.create_index(coupon_id_index, "coupons", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_coupons_id"), table_name="coupons")
    op.drop_table("coupons")
