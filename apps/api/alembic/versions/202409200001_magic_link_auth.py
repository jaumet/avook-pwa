"""Add user and magic link token tables."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "202409200001"
down_revision = "202409180001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tables required for magic link authentication."""

    op.create_table(
        "user",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column(
            "full_access",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "magic_link_token",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("used_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_ip", sa.Text(), nullable=True),
        sa.Column("created_user_agent", sa.Text(), nullable=True),
    )
    op.create_index(
        "idx_magic_link_token_user",
        "magic_link_token",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "idx_magic_link_token_hash",
        "magic_link_token",
        ["token_hash"],
        unique=False,
    )


def downgrade() -> None:
    """Drop magic link authentication tables."""

    op.drop_index("idx_magic_link_token_hash", table_name="magic_link_token")
    op.drop_index("idx_magic_link_token_user", table_name="magic_link_token")
    op.drop_table("magic_link_token")
    op.drop_table("user")
