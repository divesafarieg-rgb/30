from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4b0486e35cf7'
down_revision: Union[str, Sequence[str], None] = '7b240a5718bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('surname', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'surname')
