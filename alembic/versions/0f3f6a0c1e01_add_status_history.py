"""add status history

Revision ID: 0f3f6a0c1e01
Revises: ee96e2b63bcc
Create Date: 2026-06-01 13:43:29.603791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0f3f6a0c1e01'
down_revision: Union[str, Sequence[str], None] = 'ee96e2b63bcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    application_status = postgresql.ENUM(
        "draft",
        "applied",
        "screening",
        "interview",
        "technical_interview",
        "offer",
        "rejected",
        "withdrawn",
        name="application_status",
        create_type=False,
    )

    op.create_table(
        "status_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("old_status", application_status, nullable=False),
        sa.Column("new_status", application_status, nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["job_applications.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_status_history_application_id"), "status_history", ["application_id"])
    op.create_index(op.f("ix_status_history_id"), "status_history", ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_status_history_id"), table_name="status_history")
    op.drop_index(op.f("ix_status_history_application_id"), table_name="status_history")
    op.drop_table("status_history")
