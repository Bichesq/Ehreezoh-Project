"""Initial schema - Create all tables for Ehreezoh platform

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-18

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('phone_hash', sa.String(255), nullable=False),
        sa.Column('firebase_uid', sa.String(128), nullable=False),
        sa.Column('full_name', sa.String(100)),
        sa.Column('email', sa.String(255)),
        sa.Column('profile_photo_url', sa.String(500)),
        sa.Column('language_preference', sa.String(5), server_default='fr'),
        sa.Column('is_passenger', sa.Boolean(), server_default='true'),
        sa.Column('is_driver', sa.Boolean(), server_default='false'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_banned', sa.Boolean(), server_default='false'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('last_login_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone_number'),
        sa.UniqueConstraint('phone_hash'),
        sa.UniqueConstraint('firebase_uid')
    )
    op.create_index('idx_users_firebase_uid', 'users', ['firebase_uid'])
    op.create_index('idx_users_phone_hash', 'users', ['phone_hash'])
    
    # Create drivers table
    op.create_table(
        'drivers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('driver_license_number', sa.String(50), nullable=False),
        sa.Column('driver_license_photo_url', sa.String(500)),
        sa.Column('national_id_number', sa.String(50)),
        sa.Column('national_id_photo_url', sa.String(500)),
        sa.Column('vehicle_type', sa.String(20), nullable=False),
        sa.Column('vehicle_make', sa.String(50)),
        sa.Column('vehicle_model', sa.String(50)),
        sa.Column('vehicle_year', sa.Integer()),
        sa.Column('vehicle_color', sa.String(30)),
        sa.Column('vehicle_plate_number', sa.String(20), nullable=False),
        sa.Column('vehicle_photo_url', sa.String(500)),
        sa.Column('is_online', sa.Boolean(), server_default='false'),
        sa.Column('is_available', sa.Boolean(), server_default='true'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('verification_status', sa.String(20), server_default='pending'),
        sa.Column('verification_notes', sa.String(500)),
        sa.Column('total_rides', sa.Integer(), server_default='0'),
        sa.Column('completed_rides', sa.Integer(), server_default='0'),
        sa.Column('cancelled_rides', sa.Integer(), server_default='0'),
        sa.Column('average_rating', sa.Numeric(3, 2), server_default='0.00'),
        sa.Column('total_earnings', sa.Numeric(10, 2), server_default='0.00'),
        sa.Column('current_location', geoalchemy2.Geography(geometry_type='POINT', srid=4326)),
        sa.Column('current_latitude', sa.Numeric(10, 8)),
        sa.Column('current_longitude', sa.Numeric(11, 8)),
        sa.Column('last_location_update', sa.DateTime()),
        sa.Column('accepts_moto_requests', sa.Boolean(), server_default='true'),
        sa.Column('accepts_car_requests', sa.Boolean(), server_default='true'),
        sa.Column('max_pickup_distance_km', sa.Integer(), server_default='5'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('approved_at', sa.DateTime()),
        sa.Column('last_online_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('driver_license_number'),
        sa.UniqueConstraint('vehicle_plate_number')
    )
    op.create_index('idx_drivers_user_id', 'drivers', ['user_id'])
    op.create_index('idx_drivers_is_online', 'drivers', ['is_online'])
    op.create_index('idx_drivers_is_available', 'drivers', ['is_available'])
    op.create_index('idx_drivers_vehicle_type', 'drivers', ['vehicle_type'])
    op.create_index('idx_drivers_verification_status', 'drivers', ['verification_status'])
    # Use IF NOT EXISTS for spatial index
    op.execute('CREATE INDEX IF NOT EXISTS idx_drivers_current_location ON drivers USING GIST(current_location)')
    
    # Create rides table
    op.create_table(
        'rides',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('passenger_id', sa.String()),
        sa.Column('driver_id', sa.String()),
        sa.Column('ride_type', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='requested'),
        sa.Column('pickup_location', geoalchemy2.Geography(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('pickup_latitude', sa.Numeric(10, 8), nullable=False),
        sa.Column('pickup_longitude', sa.Numeric(11, 8), nullable=False),
        sa.Column('pickup_address', sa.Text()),
        sa.Column('dropoff_location', geoalchemy2.Geography(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('dropoff_latitude', sa.Numeric(10, 8), nullable=False),
        sa.Column('dropoff_longitude', sa.Numeric(11, 8), nullable=False),
        sa.Column('dropoff_address', sa.Text()),
        sa.Column('estimated_fare', sa.Numeric(10, 2)),
        sa.Column('offered_fare', sa.Numeric(10, 2)),
        sa.Column('counter_offer_fare', sa.Numeric(10, 2)),
        sa.Column('final_fare', sa.Numeric(10, 2)),
        sa.Column('payment_method', sa.String(20)),
        sa.Column('payment_status', sa.String(20), server_default='pending'),
        sa.Column('payment_transaction_id', sa.String(100)),
        sa.Column('estimated_distance_km', sa.Numeric(6, 2)),
        sa.Column('estimated_duration_minutes', sa.Integer()),
        sa.Column('actual_distance_km', sa.Numeric(6, 2)),
        sa.Column('actual_duration_minutes', sa.Integer()),
        sa.Column('passenger_rating', sa.Integer()),
        sa.Column('driver_rating', sa.Integer()),
        sa.Column('passenger_review', sa.Text()),
        sa.Column('driver_review', sa.Text()),
        sa.Column('cancelled_by', sa.String(20)),
        sa.Column('cancellation_reason', sa.Text()),
        sa.Column('cancellation_fee', sa.Numeric(10, 2), server_default='0.00'),
        sa.Column('requested_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('accepted_at', sa.DateTime()),
        sa.Column('driver_arrived_at', sa.DateTime()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('cancelled_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['passenger_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ondelete='SET NULL')
    )
    op.create_index('idx_rides_passenger_id', 'rides', ['passenger_id'])
    op.create_index('idx_rides_driver_id', 'rides', ['driver_id'])
    op.create_index('idx_rides_status', 'rides', ['status'])
    op.create_index('idx_rides_payment_status', 'rides', ['payment_status'])
    op.create_index('idx_rides_requested_at', 'rides', ['requested_at'], postgresql_ops={'requested_at': 'DESC'})
    op.execute('CREATE INDEX IF NOT EXISTS idx_rides_pickup_location ON rides USING GIST(pickup_location)')
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('ride_id', sa.String(), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='XAF'),
        sa.Column('payment_method', sa.String(20), nullable=False),
        sa.Column('phone_number', sa.String(20)),
        sa.Column('transaction_id', sa.String(100)),
        sa.Column('external_reference', sa.String(100)),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('failure_reason', sa.Text()),
        sa.Column('platform_commission', sa.Numeric(10, 2)),
        sa.Column('driver_payout', sa.Numeric(10, 2)),
        sa.Column('payout_status', sa.String(20), server_default='pending'),
        sa.Column('payout_transaction_id', sa.String(100)),
        sa.Column('payout_completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('transaction_id')
    )
    op.create_index('idx_payments_ride_id', 'payments', ['ride_id'])
    op.create_index('idx_payments_status', 'payments', ['status'])
    op.create_index('idx_payments_transaction_id', 'payments', ['transaction_id'])
    op.create_index('idx_payments_payout_status', 'payments', ['payout_status'])
    
    # Create driver_ratings table
    op.create_table(
        'driver_ratings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('ride_id', sa.String(), nullable=False),
        sa.Column('driver_id', sa.String(), nullable=False),
        sa.Column('passenger_id', sa.String()),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('review', sa.Text()),
        sa.Column('cleanliness_rating', sa.Integer()),
        sa.Column('driving_rating', sa.Integer()),
        sa.Column('professionalism_rating', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['passenger_id'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('ride_id')
    )
    op.create_index('idx_driver_ratings_driver_id', 'driver_ratings', ['driver_id'])
    op.create_index('idx_driver_ratings_rating', 'driver_ratings', ['rating'])
    
    # Create passenger_ratings table
    op.create_table(
        'passenger_ratings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('ride_id', sa.String(), nullable=False),
        sa.Column('passenger_id', sa.String(), nullable=False),
        sa.Column('driver_id', sa.String()),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('review', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['passenger_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('ride_id')
    )
    op.create_index('idx_passenger_ratings_passenger_id', 'passenger_ratings', ['passenger_id'])


def downgrade() -> None:
    op.drop_table('passenger_ratings')
    op.drop_table('driver_ratings')
    op.drop_table('payments')
    op.drop_table('rides')
    op.drop_table('drivers')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS postgis')
