"""Update user_uid foreign key type

Revision ID: f2db8f4d0f99
Revises: 
Create Date: 2024-10-02 22:33:49.112182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f2db8f4d0f99'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('user_uid', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'books', 'users', ['user_uid'], ['uid'], ondelete='SET NULL')
    op.drop_column('books', 'role')
    op.add_column('users', sa.Column('role', sa.VARCHAR(length=20), server_default=sa.text("'user'"), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'role')
    op.add_column('books', sa.Column('role', sa.VARCHAR(length=20), server_default=sa.text('USER'), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'books', type_='foreignkey')
    op.drop_column('books', 'user_uid')
    # ### end Alembic commands ###
