"""add application filter indexes

Revision ID: 7c3b9d2e4f81
Revises: 0f3f6a0c1e01
Create Date: 2026-06-02 02:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c3b9d2e4f81"
down_revision: Union[str, Sequence[str], None] = "0f3f6a0c1e01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLE_NAME = "job_applications"
INDEXES = {
    "ix_job_applications_applied_date": ["applied_date"],
    "ix_job_applications_created_at": ["created_at"],
}


def get_existing_index_names() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(TABLE_NAME)}


def upgrade() -> None:
    """Upgrade schema."""
    existing_indexes = get_existing_index_names()
    for index_name, columns in INDEXES.items():
        if index_name not in existing_indexes:
            op.create_index(index_name, TABLE_NAME, columns)


def downgrade() -> None:
    """Downgrade schema."""
    existing_indexes = get_existing_index_names()
    for index_name in INDEXES:
        if index_name in existing_indexes:
            op.drop_index(index_name, table_name=TABLE_NAME)
