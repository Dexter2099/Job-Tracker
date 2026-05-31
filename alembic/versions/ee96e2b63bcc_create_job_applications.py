"""create job applications

Revision ID: ee96e2b63bcc
Revises: 
Create Date: 2026-05-31 10:54:50.401816

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee96e2b63bcc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    application_status = sa.Enum(
        "draft",
        "applied",
        "screening",
        "interview",
        "technical_interview",
        "offer",
        "rejected",
        "withdrawn",
        name="application_status",
    )
    application_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "job_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company", sa.String(length=120), nullable=False),
        sa.Column("role_title", sa.String(length=160), nullable=False),
        sa.Column("location", sa.String(length=160), nullable=True),
        sa.Column("job_url", sa.String(length=500), nullable=True),
        sa.Column("status", application_status, nullable=False),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("salary_range", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("follow_up_date", sa.Date(), nullable=True),
        sa.Column("applied_date", sa.Date(), nullable=True),
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
    )
    op.create_index(op.f("ix_job_applications_company"), "job_applications", ["company"])
    op.create_index(op.f("ix_job_applications_follow_up_date"), "job_applications", ["follow_up_date"])
    op.create_index(op.f("ix_job_applications_id"), "job_applications", ["id"])
    op.create_index(op.f("ix_job_applications_status"), "job_applications", ["status"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_job_applications_status"), table_name="job_applications")
    op.drop_index(op.f("ix_job_applications_id"), table_name="job_applications")
    op.drop_index(op.f("ix_job_applications_follow_up_date"), table_name="job_applications")
    op.drop_index(op.f("ix_job_applications_company"), table_name="job_applications")
    op.drop_table("job_applications")
    sa.Enum(name="application_status").drop(op.get_bind(), checkfirst=True)
