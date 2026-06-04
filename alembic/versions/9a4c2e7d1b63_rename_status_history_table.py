"""rename status history table

Revision ID: 9a4c2e7d1b63
Revises: 7c3b9d2e4f81
Create Date: 2026-06-04 04:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9a4c2e7d1b63"
down_revision: Union[str, Sequence[str], None] = "7c3b9d2e4f81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


OLD_TABLE_NAME = "status_history"
NEW_TABLE_NAME = "application_status_history"
APPLICATION_STATUS_ENUM = postgresql.ENUM(
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


def upgrade() -> None:
    """Upgrade schema."""
    dialect_name = op.get_bind().dialect.name

    op.drop_index(op.f("ix_status_history_id"), table_name=OLD_TABLE_NAME)
    op.drop_index(op.f("ix_status_history_application_id"), table_name=OLD_TABLE_NAME)
    op.rename_table(OLD_TABLE_NAME, NEW_TABLE_NAME)

    if dialect_name == "postgresql":
        op.alter_column(
            NEW_TABLE_NAME,
            "old_status",
            existing_type=APPLICATION_STATUS_ENUM,
            type_=sa.String(length=50),
            nullable=True,
            postgresql_using="old_status::text",
        )
        op.alter_column(
            NEW_TABLE_NAME,
            "new_status",
            existing_type=APPLICATION_STATUS_ENUM,
            type_=sa.String(length=50),
            existing_nullable=False,
            postgresql_using="new_status::text",
        )
    else:
        with op.batch_alter_table(NEW_TABLE_NAME, recreate="always") as batch_op:
            batch_op.alter_column(
                "old_status",
                existing_type=sa.String(),
                type_=sa.String(length=50),
                nullable=True,
            )
            batch_op.alter_column(
                "new_status",
                existing_type=sa.String(),
                type_=sa.String(length=50),
                existing_nullable=False,
            )

    op.create_index(
        op.f("ix_application_status_history_id"),
        NEW_TABLE_NAME,
        ["id"],
    )
    op.create_index(
        op.f("ix_application_status_history_application_id"),
        NEW_TABLE_NAME,
        ["application_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    dialect_name = op.get_bind().dialect.name

    op.drop_index(op.f("ix_application_status_history_id"), table_name=NEW_TABLE_NAME)
    op.drop_index(
        op.f("ix_application_status_history_application_id"),
        table_name=NEW_TABLE_NAME,
    )

    op.execute(
        sa.text(
            "UPDATE application_status_history "
            "SET old_status = 'draft' "
            "WHERE old_status IS NULL"
        )
    )
    if dialect_name == "postgresql":
        op.alter_column(
            NEW_TABLE_NAME,
            "new_status",
            existing_type=sa.String(length=50),
            type_=APPLICATION_STATUS_ENUM,
            existing_nullable=False,
            postgresql_using="new_status::application_status",
        )
        op.alter_column(
            NEW_TABLE_NAME,
            "old_status",
            existing_type=sa.String(length=50),
            type_=APPLICATION_STATUS_ENUM,
            nullable=False,
            postgresql_using="old_status::application_status",
        )
    else:
        with op.batch_alter_table(NEW_TABLE_NAME, recreate="always") as batch_op:
            batch_op.alter_column(
                "new_status",
                existing_type=sa.String(length=50),
                type_=sa.String(),
                existing_nullable=False,
            )
            batch_op.alter_column(
                "old_status",
                existing_type=sa.String(length=50),
                type_=sa.String(),
                nullable=False,
            )

    op.rename_table(NEW_TABLE_NAME, OLD_TABLE_NAME)
    op.create_index(op.f("ix_status_history_id"), OLD_TABLE_NAME, ["id"])
    op.create_index(
        op.f("ix_status_history_application_id"),
        OLD_TABLE_NAME,
        ["application_id"],
    )
