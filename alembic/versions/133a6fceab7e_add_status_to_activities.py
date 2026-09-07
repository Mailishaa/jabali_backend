
"""add status to activities

Revision ID: add_activity_status
Revises: e834ad838c39
Create Date: 2026-09-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_activity_status"
down_revision: Union[str, Sequence[str], None] = "e834ad838c39"
branch_labels = None
depends_on = None


activity_status = sa.Enum(
    "UPCOMING",
    "COMPLETED",
    "DID_NOT_HAPPEN",
    name="activitystatus",
)


def upgrade() -> None:
    activity_status.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "activities",
        sa.Column(
            "status",
            activity_status,
            nullable=False,
            server_default="UPCOMING",
        ),
    )

    op.alter_column(
        "activities",
        "status",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("activities", "status")
    activity_status.drop(op.get_bind(), checkfirst=True)

