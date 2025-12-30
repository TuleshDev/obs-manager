"""insert initial scenarios

Revision ID: 3b2f9c7a12ef
Revises: c99588715a61
Create Date: 2025-12-29 18:35:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b2f9c7a12ef'
down_revision: Union[str, Sequence[str], None] = 'c99588715a61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    metadata = sa.MetaData()

    scenarios = sa.Table(
        "scenarios",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100)),
        sa.Column("description", sa.Text),
    )

    bind.execute(
        scenarios.insert().values([
            {
                "name": "Streaming",
                "description": "Setup Obs Studio for streaming"
            },
            {
                "name": "Math",
                "description": "Setup Obs Studio for math lessons"
            }
        ])
    )


def downgrade() -> None:
    bind = op.get_bind()
    metadata = sa.MetaData()

    scenarios = sa.Table(
        "scenarios",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100)),
    )

    bind.execute(
        scenarios.delete().where(scenarios.c.name.in_(["Streaming", "Math"]))
    )
