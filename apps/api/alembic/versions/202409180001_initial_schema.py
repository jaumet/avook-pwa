"""Initial database schema for Audiovook."""

from __future__ import annotations

import datetime
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "202409180001"
down_revision = None
branch_labels = None
depends_on = None

qr_status_enum = postgresql.ENUM(
    "new",
    "active",
    "blocked",
    name="qr_status",
    create_type=False,
)
account_provider_enum = postgresql.ENUM(
    "google",
    "apple",
    "otp",
    "guest",
    name="account_provider",
    create_type=False,
)


def upgrade() -> None:
    """Apply the initial schema."""

    bind = op.get_bind()
    qr_status_enum.create(bind, checkfirst=True)
    account_provider_enum.create(bind, checkfirst=True)

    op.create_table(
        "qr_code",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("token", sa.Text(), nullable=False, unique=True),
        sa.Column("status", qr_status_enum, nullable=False, server_default="new"),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("batch_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("registered_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "max_reactivations",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("999"),
        ),
        sa.Column("cooldown_until", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("idx_qr_token", "qr_code", ["token"], unique=False)

    op.create_table(
        "account",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.Text(), nullable=True, unique=True),
        sa.Column("provider", account_provider_enum, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "device",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("account.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("ua_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "qr_binding",
        sa.Column(
            "qr_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("qr_code.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("device.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("account.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "active",
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
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index(
        "idx_binding_qr_active",
        "qr_binding",
        ["qr_id", "active"],
        unique=False,
    )

    op.create_table(
        "play_session",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "qr_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("qr_code.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("device.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("ended_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("ip_hash", sa.Text(), nullable=False),
    )

    op.create_table(
        "listening_progress",
        sa.Column(
            "qr_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("qr_code.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("account.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("device.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("track_id", sa.Text(), primary_key=True, nullable=False),
        sa.Column("position_ms", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "idx_progress_updated_at",
        "listening_progress",
        ["updated_at"],
        unique=False,
    )

    qr_code_table = sa.table(
        "qr_code",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("token", sa.Text()),
        sa.column("status", qr_status_enum),
        sa.column("product_id", sa.Integer()),
        sa.column("batch_id", sa.Integer()),
        sa.column("created_at", sa.TIMESTAMP(timezone=True)),
        sa.column("registered_at", sa.TIMESTAMP(timezone=True)),
        sa.column("max_reactivations", sa.Integer()),
        sa.column("cooldown_until", sa.TIMESTAMP(timezone=True)),
    )

    now = datetime.datetime.utcnow()
    op.bulk_insert(
        qr_code_table,
        [
            {
                "id": uuid.uuid4(),
                "token": "DEMO-ALPHA",
                "status": "new",
                "product_id": 1,
                "batch_id": 1,
                "created_at": now,
                "max_reactivations": 999,
            },
            {
                "id": uuid.uuid4(),
                "token": "DEMO-BETA",
                "status": "new",
                "product_id": 1,
                "batch_id": 1,
                "created_at": now,
                "max_reactivations": 999,
            },
            {
                "id": uuid.uuid4(),
                "token": "DEMO-GAMMA",
                "status": "new",
                "product_id": 2,
                "batch_id": 2,
                "created_at": now,
                "max_reactivations": 999,
            },
        ],
    )


def downgrade() -> None:
    """Remove the schema additions."""

    op.drop_index("idx_progress_updated_at", table_name="listening_progress")
    op.drop_table("listening_progress")

    op.drop_table("play_session")

    op.drop_index("idx_binding_qr_active", table_name="qr_binding")
    op.drop_table("qr_binding")

    op.drop_table("device")
    op.drop_table("account")

    op.drop_index("idx_qr_token", table_name="qr_code")
    op.drop_table("qr_code")

    bind = op.get_bind()
    account_provider_enum.drop(bind, checkfirst=True)
    qr_status_enum.drop(bind, checkfirst=True)
