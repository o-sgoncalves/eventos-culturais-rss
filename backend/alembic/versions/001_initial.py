"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-18
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(50), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform", sa.String(50), server_default="instagram"),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("active", sa.Boolean(), server_default="true"),
        sa.Column("last_scraped", sa.DateTime()),
        sa.Column("error_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("event_date", sa.DateTime()),
        sa.Column("event_time", sa.String(50)),
        sa.Column("location", sa.String(255)),
        sa.Column("address", sa.Text()),
        sa.Column("region", sa.String(100)),
        sa.Column("price", sa.String(100)),
        sa.Column("is_free", sa.Boolean(), server_default="false"),
        sa.Column("category", sa.String(50)),
        sa.Column("source_url", sa.Text(), unique=True),
        sa.Column("image_url", sa.Text()),
        sa.Column("approved", sa.Boolean(), server_default="false"),
        sa.Column("submitted_by_user", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("idx_events_date", "events", ["event_date"])
    op.create_index("idx_events_approved", "events", ["approved"])
    op.create_index("idx_events_category", "events", ["category"])
    op.create_index("idx_events_is_free", "events", ["is_free"])


def downgrade() -> None:
    op.drop_table("events")
    op.drop_table("sources")
    op.drop_table("users")
