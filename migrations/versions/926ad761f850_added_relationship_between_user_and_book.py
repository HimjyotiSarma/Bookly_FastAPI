"""Added relationship between User and Book

Revision ID: 926ad761f850
Revises: f2db8f4d0f99
Create Date: 2024-10-04 21:00:09.774338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '926ad761f850'
down_revision: Union[str, None] = 'f2db8f4d0f99'
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