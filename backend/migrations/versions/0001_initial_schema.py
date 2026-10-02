"""Create the initial CodeGuard schema.

Revision ID: 0001_initial_schema
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_projects_user_id", "projects", ["user_id"])

    op.create_table(
        "files",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_files_project_id", "files", ["project_id"])

    op.create_table(
        "analyses",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("file_id", sa.String(length=36), sa.ForeignKey("files.id"), nullable=True),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("findings_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
    )
    op.create_index("ix_analyses_project_id", "analyses", ["project_id"])

    op.create_table(
        "issues",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("analysis_id", sa.String(length=36), sa.ForeignKey("analyses.id"), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("line", sa.Integer(), nullable=True),
        sa.Column("file", sa.String(length=255), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_issues_analysis_id", "issues", ["analysis_id"])
    op.create_index("ix_issues_severity", "issues", ["severity"])

    op.create_table(
        "ai_reviews",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("analysis_id", sa.String(length=36), sa.ForeignKey("analyses.id"), nullable=False, unique=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("issues", sa.JSON(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("improvements", sa.JSON(), nullable=True),
        sa.Column("optimized_code", sa.Text(), nullable=True),
        sa.Column("complexity_explanation", sa.Text(), nullable=True),
        sa.Column("security_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("analysis_id", sa.String(length=36), sa.ForeignKey("analyses.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_reports_analysis_id", "reports", ["analysis_id"])


def downgrade() -> None:
    op.drop_index("ix_reports_analysis_id", table_name="reports")
    op.drop_table("reports")
    op.drop_table("ai_reviews")
    op.drop_index("ix_issues_severity", table_name="issues")
    op.drop_index("ix_issues_analysis_id", table_name="issues")
    op.drop_table("issues")
    op.drop_index("ix_analyses_project_id", table_name="analyses")
    op.drop_table("analyses")
    op.drop_index("ix_files_project_id", table_name="files")
    op.drop_table("files")
    op.drop_index("ix_projects_user_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
