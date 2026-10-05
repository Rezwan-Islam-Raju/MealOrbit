"""add restaurant id to food category

Revision ID: 10a071a22830
Revises: 7277acc8f603
Create Date: 2026-10-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7277acc8f603"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        "food_category",
        sa.Column(
            "restaurant_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.create_index(
        "ix_food_category_restaurant_id",
        "food_category",
        ["restaurant_id"],
        unique=False
    )

    op.create_foreign_key(
        "fk_food_category_restaurant_id",
        "food_category",
        "restaurants",
        ["restaurant_id"],
        ["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_food_category_restaurant_id",
        "food_category",
        type_="foreignkey"
    )

    op.drop_index(
        "ix_food_category_restaurant_id",
        table_name="food_category"
    )

    op.drop_column(
        "food_category",
        "restaurant_id"
    )