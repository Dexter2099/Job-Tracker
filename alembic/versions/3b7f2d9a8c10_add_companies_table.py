"""add companies table

Revision ID: 3b7f2d9a8c10
Revises: 9a4c2e7d1b63
Create Date: 2026-06-04 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3b7f2d9a8c10"
down_revision: Union[str, Sequence[str], None] = "9a4c2e7d1b63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("website", sa.String(length=500), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_companies_created_at"), "companies", ["created_at"])
    op.create_index(op.f("ix_companies_id"), "companies", ["id"])

    op.add_column("job_applications", sa.Column("company_id", sa.Integer()))
    op.create_index(
        op.f("ix_job_applications_company_id"),
        "job_applications",
        ["company_id"],
    )

    op.execute(
        sa.text(
            "INSERT INTO companies (name) "
            "SELECT DISTINCT company FROM job_applications "
            "WHERE company IS NOT NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE job_applications "
            "SET company_id = companies.id "
            "FROM companies "
            "WHERE job_applications.company = companies.name"
        )
    )

    op.alter_column("job_applications", "company_id", nullable=False)
    op.create_foreign_key(
        "fk_job_applications_company_id_companies",
        "job_applications",
        "companies",
        ["company_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_job_applications_company_id_companies",
        "job_applications",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_job_applications_company_id"),
        table_name="job_applications",
    )
    op.drop_column("job_applications", "company_id")
    op.drop_index(op.f("ix_companies_id"), table_name="companies")
    op.drop_index(op.f("ix_companies_created_at"), table_name="companies")
    op.drop_table("companies")
