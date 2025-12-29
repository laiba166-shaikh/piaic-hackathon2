"""create tasks table

Revision ID: 001
Revises:
Create Date: 2025-12-29

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Create tasks table with user isolation and soft delete support.

    Schema:
        - id: Primary key (auto-increment)
        - user_id: VARCHAR(255), indexed (from JWT token)
        - title: VARCHAR(200), required
        - description: TEXT, nullable
        - completed: BOOLEAN, default FALSE
        - deleted_at: TIMESTAMP, nullable, indexed (soft delete)
        - created_at: TIMESTAMP, auto-generated
        - updated_at: TIMESTAMP, auto-updated

    Indexes:
        - idx_tasks_user_id: For filtering by user
        - idx_tasks_deleted_at: For filtering active vs deleted
        - idx_tasks_user_deleted: Composite index for common queries
    """
    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.VARCHAR(length=255), nullable=False),
        sa.Column("title", sa.VARCHAR(length=200), nullable=False),
        sa.Column("description", sa.TEXT(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("deleted_at", sa.TIMESTAMP(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("idx_tasks_user_id", "tasks", ["user_id"])
    op.create_index("idx_tasks_deleted_at", "tasks", ["deleted_at"])
    op.create_index("idx_tasks_user_deleted", "tasks", ["user_id", "deleted_at"])

    # Create trigger to auto-update updated_at timestamp
    # PostgreSQL specific trigger
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )

    op.execute(
        """
        CREATE TRIGGER update_tasks_updated_at
        BEFORE UPDATE ON tasks
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
        """
    )


def downgrade() -> None:
    """Drop tasks table and trigger."""
    # Drop trigger first
    op.execute("DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop indexes
    op.drop_index("idx_tasks_user_deleted", table_name="tasks")
    op.drop_index("idx_tasks_deleted_at", table_name="tasks")
    op.drop_index("idx_tasks_user_id", table_name="tasks")

    # Drop table
    op.drop_table("tasks")
