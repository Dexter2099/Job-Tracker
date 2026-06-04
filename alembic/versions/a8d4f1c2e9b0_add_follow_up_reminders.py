"""add follow up reminders

Revision ID: a8d4f1c2e9b0
Revises: 6e4a1c7b9d20
Create Date: 2026-06-04 16:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a8d4f1c2e9b0"
down_revision: Union[str, Sequence[str], None] = "6e4a1c7b9d20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "follow_up_reminders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("reminder_date", sa.Date(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("completed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["job_applications.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_follow_up_reminders_application_id"),
        "follow_up_reminders",
        ["application_id"],
    )
    op.create_index(
        op.f("ix_follow_up_reminders_completed"),
        "follow_up_reminders",
        ["completed"],
    )
    op.create_index(
        op.f("ix_follow_up_reminders_created_at"),
        "follow_up_reminders",
        ["created_at"],
    )
    op.create_index(
        op.f("ix_follow_up_reminders_id"),
        "follow_up_reminders",
        ["id"],
    )
    op.create_index(
        op.f("ix_follow_up_reminders_reminder_date"),
        "follow_up_reminders",
        ["reminder_date"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_follow_up_reminders_reminder_date"),
        table_name="follow_up_reminders",
    )
    op.drop_index(op.f("ix_follow_up_reminders_id"), table_name="follow_up_reminders")
    op.drop_index(
        op.f("ix_follow_up_reminders_created_at"),
        table_name="follow_up_reminders",
    )
    op.drop_index(
        op.f("ix_follow_up_reminders_completed"),
        table_name="follow_up_reminders",
    )
    op.drop_index(
        op.f("ix_follow_up_reminders_application_id"),
        table_name="follow_up_reminders",
    )
    op.drop_table("follow_up_reminders")
