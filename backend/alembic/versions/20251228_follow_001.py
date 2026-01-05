"""Add user_follows table

Revision ID: follow_001
Revises: social_001
Create Date: 2024-12-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'follow_001'
down_revision = 'social_001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_follows',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('follower_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('followed_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Create index for fast lookups
    op.create_index('ix_user_follows_follower_id', 'user_follows', ['follower_id'])
    op.create_index('ix_user_follows_followed_id', 'user_follows', ['followed_id'])
    # Unique constraint to prevent duplicate follows
    op.create_unique_constraint('uq_user_follows_pair', 'user_follows', ['follower_id', 'followed_id'])


def downgrade():
    op.drop_constraint('uq_user_follows_pair', 'user_follows')
    op.drop_index('ix_user_follows_followed_id')
    op.drop_index('ix_user_follows_follower_id')
    op.drop_table('user_follows')
