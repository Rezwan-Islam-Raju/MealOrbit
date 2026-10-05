"""add_user_role

Revision ID: 91f5ff8860f6
Revises: c6ff1e4816df
Create Date: 2026-09-29 12:21:50.854219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91f5ff8860f6'
down_revision: Union[str, Sequence[str], None] = 'c6ff1e4816df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    user_role_enum = sa.Enum(
        'customer',
        'restaurant_owner',
        'rider',
        'admin',
        name='userroleenum'
    )

    # Create PostgreSQL ENUM type first
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Convert users.role from VARCHAR to ENUM
    op.alter_column(
        'users',
        'role',
        existing_type=sa.VARCHAR(length=30),
        type_=user_role_enum,
        existing_nullable=False,
        postgresql_using='role::userroleenum'
    )

    # Drop old index
    op.drop_index(
        op.f('ix_users_role'),
        table_name='users'
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Recreate index
    op.create_index(
        op.f('ix_users_role'),
        'users',
        ['role'],
        unique=False
    )

    # Convert ENUM back to VARCHAR
    op.alter_column(
        'users',
        'role',
        existing_type=sa.Enum(
            'customer',
            'restaurant_owner',
            'rider',
            'admin',
            name='userroleenum'
        ),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
        postgresql_using='role::text'
    )

    # Remove PostgreSQL ENUM type
    sa.Enum(
        'customer',
        'restaurant_owner',
        'rider',
        'admin',
        name='userroleenum'
    ).drop(op.get_bind(), checkfirst=True)