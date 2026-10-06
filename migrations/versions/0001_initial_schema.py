"""Initial schema: participants, event entries, hackathon teams and members.

Revision ID: 0001
Revises:
Create Date: 2026-10-06

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "hackathon_teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_name", sa.String(length=60), nullable=False),
        sa.Column("leader_name", sa.String(length=80), nullable=False),
        sa.Column("college", sa.String(length=120), nullable=False),
        sa.Column("department", sa.String(length=40), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("mobile", sa.String(length=10), nullable=False),
        sa.Column("project_title", sa.String(length=120), nullable=False),
        sa.Column("domain", sa.String(length=60), nullable=False),
        sa.Column("needs_technical_help", sa.Boolean(), nullable=False),
        sa.Column("needs_accommodation", sa.Boolean(), nullable=False),
        sa.Column("heard_from", sa.String(length=40), nullable=False),
        sa.Column("abstract_path", sa.String(length=80), nullable=False),
        sa.Column("abstract_filename", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mobile"),
        sa.UniqueConstraint("team_name"),
    )
    with op.batch_alter_table("hackathon_teams", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_hackathon_teams_email"), ["email"], unique=True)

    op.create_table(
        "participants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("college", sa.String(length=120), nullable=False),
        sa.Column("department", sa.String(length=40), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("mobile", sa.String(length=10), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mobile"),
    )
    with op.batch_alter_table("participants", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_participants_email"), ["email"], unique=True)

    op.create_table(
        "event_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("event_slug", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["participant_id"], ["participants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("participant_id", "event_slug"),
    )
    with op.batch_alter_table("event_entries", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_event_entries_event_slug"), ["event_slug"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_event_entries_participant_id"), ["participant_id"], unique=False
        )

    op.create_table(
        "team_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["hackathon_teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("team_members", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_team_members_team_id"), ["team_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("team_members", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_team_members_team_id"))

    op.drop_table("team_members")
    with op.batch_alter_table("event_entries", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_event_entries_participant_id"))
        batch_op.drop_index(batch_op.f("ix_event_entries_event_slug"))

    op.drop_table("event_entries")
    with op.batch_alter_table("participants", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_participants_email"))

    op.drop_table("participants")
    with op.batch_alter_table("hackathon_teams", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_hackathon_teams_email"))

    op.drop_table("hackathon_teams")
