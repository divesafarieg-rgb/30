from alembic import op
import sqlalchemy as sa

revision = '803388c8eeec'
down_revision = '791ecb0eb2d2'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('users', 'has_sale')

def downgrade():
    op.add_column('users', sa.Column('has_sale', sa.Boolean(), nullable=True))