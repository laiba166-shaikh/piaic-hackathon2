"""add completed index to tasks

Revision ID: 002
Revises: 001
Create Date: 2026-04-05

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add index on tasks.completed for status-based filtering."""
    op.create_index("idx_tasks_completed", "tasks", ["completed"])


def downgrade() -> None:
    """Remove completed index."""
    op.drop_index("idx_tasks_completed", table_name="tasks")
