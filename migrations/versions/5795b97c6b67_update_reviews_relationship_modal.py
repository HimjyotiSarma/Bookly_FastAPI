"""Update Reviews relationship modal

Revision ID: 5795b97c6b67
Revises: fdb682ec1046
Create Date: 2024-10-14 22:23:14.116351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5795b97c6b67'
down_revision: Union[str, None] = 'fdb682ec1046'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###