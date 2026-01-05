"""Add social tables for Thanks and Comments

Revision ID: social_001
Revises: community_phase2_001
Create Date: 2024-12-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'social_001'
down_revision = 'community_phase2_001'
branch_labels = None
depends_on = None


def upgrade():
    # Create incident_thanks table
    op.create_table(
        'incident_thanks',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('incident_id', sa.String(), sa.ForeignKey('incidents.id'), nullable=False),
        sa.Column('reporter_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('thanker_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Create incident_comments table
    op.create_table(
        'incident_comments',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('incident_id', sa.String(), sa.ForeignKey('incidents.id'), nullable=False),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('upvotes', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Create comment_upvotes table
    op.create_table(
        'comment_upvotes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('comment_id', sa.String(), sa.ForeignKey('incident_comments.id'), nullable=False),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Create indexes
    op.create_index('ix_incident_thanks_incident_id', 'incident_thanks', ['incident_id'])
    op.create_index('ix_incident_thanks_reporter_id', 'incident_thanks', ['reporter_id'])
    op.create_index('ix_incident_comments_incident_id', 'incident_comments', ['incident_id'])
    op.create_index('ix_comment_upvotes_comment_id', 'comment_upvotes', ['comment_id'])


def downgrade():
    op.drop_index('ix_comment_upvotes_comment_id')
    op.drop_index('ix_incident_comments_incident_id')
    op.drop_index('ix_incident_thanks_reporter_id')
    op.drop_index('ix_incident_thanks_incident_id')
    op.drop_table('comment_upvotes')
    op.drop_table('incident_comments')
    op.drop_table('incident_thanks')
