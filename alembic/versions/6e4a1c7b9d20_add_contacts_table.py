"""add contacts table

Revision ID: 6e4a1c7b9d20
Revises: 3b7f2d9a8c10
Create Date: 2026-06-04 15:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6e4a1c7b9d20"
down_revision: Union[str, Sequence[str], None] = "3b7f2d9a8c10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=80), nullable=True),
        sa.Column("role_title", sa.String(length=160), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_contacts_company_id"), "contacts", ["company_id"])
    op.create_index(op.f("ix_contacts_created_at"), "contacts", ["created_at"])
    op.create_index(op.f("ix_contacts_email"), "contacts", ["email"])
    op.create_index(op.f("ix_contacts_id"), "contacts", ["id"])

    op.add_column("job_applications", sa.Column("contact_id", sa.Integer()))
    op.add_column(
        "job_applications",
        sa.Column("contact_name", sa.String(length=160), nullable=True),
    )
    op.add_column(
        "job_applications",
        sa.Column("contact_email", sa.String(length=255), nullable=True),
    )
    op.create_index(
        op.f("ix_job_applications_contact_id"),
        "job_applications",
        ["contact_id"],
    )
    op.create_foreign_key(
        "fk_job_applications_contact_id_contacts",
        "job_applications",
        "contacts",
        ["contact_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_job_applications_contact_id_contacts",
        "job_applications",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_job_applications_contact_id"),
        table_name="job_applications",
    )
    op.drop_column("job_applications", "contact_email")
    op.drop_column("job_applications", "contact_name")
    op.drop_column("job_applications", "contact_id")
    op.drop_index(op.f("ix_contacts_id"), table_name="contacts")
    op.drop_index(op.f("ix_contacts_email"), table_name="contacts")
    op.drop_index(op.f("ix_contacts_created_at"), table_name="contacts")
    op.drop_index(op.f("ix_contacts_company_id"), table_name="contacts")
    op.drop_table("contacts")
