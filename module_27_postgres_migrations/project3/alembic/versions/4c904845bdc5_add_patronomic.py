from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '4c904845bdc5'
down_revision: Union[str, Sequence[str], None] = '803388c8eeec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('patronomic', sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'patronomic')