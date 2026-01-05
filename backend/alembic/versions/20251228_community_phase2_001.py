"""Add community tables for Phase 2

Revision ID: community_phase2_001
Revises: community_stats_001
Create Date: 2024-12-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'community_phase2_001'
down_revision = 'community_stats_001'
branch_labels = None
depends_on = None


def upgrade():
    # Create cities table
    op.create_table(
        'cities',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('country', sa.String(100), default='Cameroon'),
        sa.Column('active_contributors', sa.Integer(), default=0),
        sa.Column('total_reports', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Create neighborhoods table
    op.create_table(
        'neighborhoods',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('city_id', sa.String(), sa.ForeignKey('cities.id'), nullable=False),
        sa.Column('geojson', JSONB, nullable=True),
        sa.Column('center_lat', sa.Numeric(10, 6), nullable=True),
        sa.Column('center_lng', sa.Numeric(10, 6), nullable=True),
        sa.Column('active_contributors', sa.Integer(), default=0),
        sa.Column('total_reports', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Create user_neighborhoods table (many-to-many with stats)
    op.create_table(
        'user_neighborhoods',
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('neighborhood_id', sa.String(), sa.ForeignKey('neighborhoods.id'), primary_key=True),
        sa.Column('is_home', sa.Boolean(), default=False),
        sa.Column('report_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Create incident_verifications table
    op.create_table(
        'incident_verifications',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('incident_id', sa.String(), sa.ForeignKey('incidents.id'), nullable=False),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('verification_type', sa.String(20), nullable=False),
        sa.Column('weight', sa.Numeric(5, 2), default=1.0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Create indexes for faster queries
    op.create_index('ix_incident_verifications_incident_id', 'incident_verifications', ['incident_id'])
    op.create_index('ix_neighborhoods_city_id', 'neighborhoods', ['city_id'])
    
    # Seed initial cities for Cameroon
    op.execute("""
        INSERT INTO cities (id, name, country) VALUES
        ('douala-001', 'Douala', 'Cameroon'),
        ('yaounde-001', 'Yaoundé', 'Cameroon'),
        ('bamenda-001', 'Bamenda', 'Cameroon'),
        ('bafoussam-001', 'Bafoussam', 'Cameroon'),
        ('garoua-001', 'Garoua', 'Cameroon')
    """)
    
    # Seed some initial neighborhoods for Douala
    op.execute("""
        INSERT INTO neighborhoods (id, name, city_id, center_lat, center_lng) VALUES
        ('akwa-001', 'Akwa', 'douala-001', 4.0511, 9.7679),
        ('bonapriso-001', 'Bonapriso', 'douala-001', 4.0242, 9.6919),
        ('bonamoussadi-001', 'Bonamoussadi', 'douala-001', 4.0689, 9.7203),
        ('deido-001', 'Deido', 'douala-001', 4.0567, 9.7089),
        ('bali-001', 'Bali', 'douala-001', 4.0411, 9.6989)
    """)
    
    # Seed some initial neighborhoods for Yaoundé
    op.execute("""
        INSERT INTO neighborhoods (id, name, city_id, center_lat, center_lng) VALUES
        ('bastos-001', 'Bastos', 'yaounde-001', 3.8803, 11.5089),
        ('nlongkak-001', 'Nlongkak', 'yaounde-001', 3.8667, 11.5333),
        ('messa-001', 'Messa', 'yaounde-001', 3.8667, 11.4833),
        ('essos-001', 'Essos', 'yaounde-001', 3.8667, 11.5500),
        ('mvog-mbi-001', 'Mvog-Mbi', 'yaounde-001', 3.8500, 11.5167)
    """)


def downgrade():
    op.drop_index('ix_neighborhoods_city_id')
    op.drop_index('ix_incident_verifications_incident_id')
    op.drop_table('incident_verifications')
    op.drop_table('user_neighborhoods')
    op.drop_table('neighborhoods')
    op.drop_table('cities')
