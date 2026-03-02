from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7b240a5718bc'
down_revision: Union[str, Sequence[str], None] = ('4c904845bdc5', '93fa6196b930')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
