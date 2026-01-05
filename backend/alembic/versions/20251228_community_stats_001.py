"""Add community stats to users

Revision ID: community_stats_001
Revises: b220857e9fea
Create Date: 2024-12-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'community_stats_001'
down_revision = 'b220857e9fea'
branch_labels = None
depends_on = None


def upgrade():
    # Add community stats columns to users table
    op.add_column('users', sa.Column('trust_score', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('total_reports', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('total_people_helped', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('current_streak', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('longest_streak', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('last_report_date', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('users', 'trust_score')
    op.drop_column('users', 'total_reports')
    op.drop_column('users', 'total_people_helped')
    op.drop_column('users', 'current_streak')
    op.drop_column('users', 'longest_streak')
    op.drop_column('users', 'last_report_date')
