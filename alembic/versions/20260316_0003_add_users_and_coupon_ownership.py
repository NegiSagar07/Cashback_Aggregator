"""add users table and coupon ownership

Revision ID: 20260316_0003
Revises: 20260315_0002
Create Date: 2026-03-16 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "20260316_0003"
down_revision: Union[str, None] = "20260315_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	bind = op.get_bind()
	inspector = inspect(bind)

	if not inspector.has_table("users"):
		op.create_table(
			"users",
			sa.Column("id", sa.Integer(), nullable=False),
			sa.Column("username", sa.String(), nullable=False),
			sa.Column("hashed_password", sa.String(), nullable=False),
			sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
			sa.PrimaryKeyConstraint("id"),
		)

	existing_indexes = {idx["name"] for idx in inspector.get_indexes("users")} if inspector.has_table("users") else set()
	if "ix_users_id" not in existing_indexes:
		op.create_index("ix_users_id", "users", ["id"], unique=False)
	if "ix_users_username" not in existing_indexes:
		op.create_index("ix_users_username", "users", ["username"], unique=True)

	user_columns = {col["name"] for col in inspector.get_columns("coupons")}
	if "user_id" not in user_columns:
		op.add_column("coupons", sa.Column("user_id", sa.Integer(), nullable=True))

	bind.execute(
        sa.text(
            """
            INSERT INTO users (username, hashed_password, is_active)
            SELECT CAST(:username AS VARCHAR), CAST(:hashed_password AS VARCHAR), true
            WHERE NOT EXISTS (
                SELECT 1 FROM users WHERE username = :username
            )
            """
        ),
        {"username": "legacy_owner", "hashed_password": "disabled_migrated_account"},
    )

	legacy_user_id = bind.execute(
		sa.text("SELECT id FROM users WHERE username = :username"),
		{"username": "legacy_owner"},
	).scalar_one()

	bind.execute(
		sa.text("UPDATE coupons SET user_id = :user_id WHERE user_id IS NULL"),
		{"user_id": legacy_user_id},
	)

	foreign_keys = {fk["name"] for fk in inspector.get_foreign_keys("coupons") if fk.get("name")}
	if "fk_coupons_user_id_users" not in foreign_keys:
		op.create_foreign_key(
			"fk_coupons_user_id_users",
			"coupons",
			"users",
			["user_id"],
			["id"],
		)

	coupon_indexes = {idx["name"] for idx in inspector.get_indexes("coupons")}
	if "ix_coupons_user_id" not in coupon_indexes:
		op.create_index("ix_coupons_user_id", "coupons", ["user_id"], unique=False)

	op.alter_column("coupons", "user_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
	bind = op.get_bind()
	inspector = inspect(bind)

	coupon_indexes = {idx["name"] for idx in inspector.get_indexes("coupons")}
	if "ix_coupons_user_id" in coupon_indexes:
		op.drop_index("ix_coupons_user_id", table_name="coupons")

	foreign_keys = {fk["name"] for fk in inspector.get_foreign_keys("coupons") if fk.get("name")}
	if "fk_coupons_user_id_users" in foreign_keys:
		op.drop_constraint("fk_coupons_user_id_users", "coupons", type_="foreignkey")

	columns = {col["name"] for col in inspector.get_columns("coupons")}
	if "user_id" in columns:
		op.drop_column("coupons", "user_id")

	if inspector.has_table("users"):
		user_indexes = {idx["name"] for idx in inspector.get_indexes("users")}
		if "ix_users_username" in user_indexes:
			op.drop_index("ix_users_username", table_name="users")
		if "ix_users_id" in user_indexes:
			op.drop_index("ix_users_id", table_name="users")
		op.drop_table("users")