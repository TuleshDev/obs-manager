"""add nonnegative constraints to students

Revision ID: f4c9b37b7fbd
Revises: 144d0e29b519
Create Date: 2025-12-24 14:31:42.824076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4c9b37b7fbd'
down_revision: Union[str, Sequence[str], None] = '144d0e29b519'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "check_chapter_nonnegative",
        "students",
        "chapter >= 0"
    )
    op.create_check_constraint(
        "check_paragraph_nonnegative",
        "students",
        "paragraph >= 0"
    )
    op.create_check_constraint(
        "check_section_nonnegative",
        "students",
        "section >= 0"
    )
    op.create_check_constraint(
        "check_position_nonnegative",
        "students",
        "position >= 0"
    )
    op.create_check_constraint(
        "check_task_number_nonnegative",
        "students",
        "task_number >= 0"
    )

def downgrade() -> None:
    op.drop_constraint("check_chapter_nonnegative", "students", type_="check")
    op.drop_constraint("check_paragraph_nonnegative", "students", type_="check")
    op.drop_constraint("check_section_nonnegative", "students", type_="check")
    op.drop_constraint("check_position_nonnegative", "students", type_="check")
    op.drop_constraint("check_task_number_nonnegative", "students", type_="check")
