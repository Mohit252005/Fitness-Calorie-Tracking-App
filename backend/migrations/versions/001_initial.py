"""Initial: users, meals, workouts

Revision ID: 001_initial
Revises:
Create Date: 2025-02-21

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "meals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(512), nullable=True),
        sa.Column("calories", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("protein", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("carbs", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("fats", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meals_user_id"), "meals", ["user_id"], unique=False)

    op.create_table(
        "workouts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("calories_burned", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workouts_user_id"), "workouts", ["user_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_workouts_user_id"), table_name="workouts")
    op.drop_table("workouts")
    op.drop_index(op.f("ix_meals_user_id"), table_name="meals")
    op.drop_table("meals")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
