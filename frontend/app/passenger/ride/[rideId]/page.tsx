/**
 * Ride Tracking Page
 * Real-time ride status monitoring for passengers
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button, Card } from '@/components/ui';
import { RideStatusBadge } from '@/components/Ride/RideStatusBadge';
import { DriverCard } from '@/components/Driver/DriverCard';
import { RideTimeline } from '@/components/Ride/RideTimeline';
import { MapView } from '@/components/Map/MapView';
import { api, getErrorMessage } from '@/services/api';
import { geolocationService } from '@/services/geolocation';
import { useRideWebSocket } from '@/hooks/useRideWebSocket';

interface RideTrackingPageProps {
  params: {
    rideId: string;
  };
}

export default function RideTrackingPage({ params }: RideTrackingPageProps) {
  const router = useRouter();
  const { rideId } = params;

  const [ride, setRide] = useState<any>(null);
  const [driver, setDriver] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancelling, setCancelling] = useState(false);

  // WebSocket connection for real-time updates
  const { connected, rideUpdate } = useRideWebSocket(rideId);

  // Fetch ride details
  const fetchRideDetails = async () => {
    try {
      const response = await api.rides.get(rideId);
      const rideData = response.data;
      setRide(rideData);

      // If ride is completed, redirect to completion page
      if (rideData.status === 'completed') {
        router.push(`/passenger/ride/${rideId}/complete`);
      }

      setError('');
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Fetch driver details when ride is accepted
  const fetchDriverDetails = async () => {
    if (!ride || !ride.driver_id) return;

    try {
      // Driver details are included in ride response from backend
      // Extract driver info from ride data
      setDriver({
        full_name: ride.driver?.full_name || 'Driver',
        phone_number: ride.driver?.phone_number,
        profile_photo_url: ride.driver?.profile_photo_url,
        average_rating: ride.driver?.average_rating || 0,
        total_rides: ride.driver?.total_rides || 0,
        vehicle_type: ride.driver?.vehicle_type || ride.ride_type,
        vehicle_make: ride.driver?.vehicle_make,
        vehicle_model: ride.driver?.vehicle_model,
        vehicle_color: ride.driver?.vehicle_color,
        vehicle_plate_number: ride.driver?.vehicle_plate_number,
      });
    } catch (err) {
      console.error('Error fetching driver details:', err);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchRideDetails();
  }, [rideId]);

  // Handle WebSocket updates
  useEffect(() => {
    if (!rideUpdate) return;

    console.log('📨 Received ride update:', rideUpdate);

    // Update ride status
    if (rideUpdate.status) {
      setRide((prev: any) => ({
        ...prev,
        status: rideUpdate.status,
      }));

      // Redirect if completed
      if (rideUpdate.status === 'completed') {
        router.push(`/passenger/ride/${rideId}/complete`);
      }
    }

    // Update driver info
    if (rideUpdate.driver) {
      setDriver({
        full_name: rideUpdate.driver.full_name || 'Driver',
        phone_number: rideUpdate.driver.phone_number,
        profile_photo_url: rideUpdate.driver.profile_photo_url,
        average_rating: rideUpdate.driver.average_rating || 0,
        total_rides: rideUpdate.driver.total_rides || 0,
        vehicle_type: rideUpdate.driver.vehicle_type || ride?.ride_type,
        vehicle_make: rideUpdate.driver.vehicle_make,
        vehicle_model: rideUpdate.driver.vehicle_model,
        vehicle_color: rideUpdate.driver.vehicle_color,
        vehicle_plate_number: rideUpdate.driver.vehicle_plate_number,
      });
    }

    // Update driver location (for real-time tracking)
    if (rideUpdate.location) {
      // TODO: Update map with driver's current location
      console.log('📍 Driver location:', rideUpdate.location);
    }
  }, [rideUpdate]);

  // Fetch driver details when ride is accepted
  useEffect(() => {
    if (ride && ride.driver_id) {
      fetchDriverDetails();
    }
  }, [ride?.driver_id]);

  // Handle cancel ride
  const handleCancelRide = async () => {
    if (!confirm('Are you sure you want to cancel this ride?')) {
      return;
    }

    setCancelling(true);
    try {
      await api.rides.cancel(rideId, 'Cancelled by passenger');
      await fetchRideDetails();
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setCancelling(false);
    }
  };

  // Calculate ETA (simplified)
  const calculateETA = () => {
    if (!ride || !driver) return undefined;

    // If ride hasn't started, calculate ETA to pickup
    if (ride.status === 'accepted' && ride.pickup_latitude && ride.pickup_longitude) {
      // Placeholder: In real app, use driver's current location
      return 5; // 5 minutes placeholder
    }

    // If ride has started, calculate ETA to destination
    if (ride.status === 'started' && ride.dropoff_latitude && ride.dropoff_longitude) {
      const distance = ride.estimated_distance_km || 5;
      return geolocationService.calculateETA(distance);
    }

    return undefined;
  };

  if (loading) {
    return (
      <main className="min-h-screen p-4 bg-bg-primary flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce">🚗</div>
          <div className="text-text-primary text-xl">Loading ride details...</div>
        </div>
      </main>
    );
  }

  if (error && !ride) {
    return (
      <main className="min-h-screen p-4 bg-bg-primary flex items-center justify-center">
        <Card className="max-w-md">
          <div className="text-center">
            <div className="text-6xl mb-4">❌</div>
            <h2 className="text-xl font-bold text-text-primary mb-2">Error</h2>
            <p className="text-text-secondary mb-4">{error}</p>
            <Button onClick={() => router.push('/dashboard')}>
              Back to Dashboard
            </Button>
          </div>
        </Card>
      </main>
    );
  }

  if (!ride) return null;

  const eta = calculateETA();

  return (
    <main className="min-h-screen p-4 bg-bg-primary">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-primary hover:text-primary-light flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>
          <h1 className="text-2xl font-bold text-text-primary">Your Ride</h1>
          <div className="w-16"></div>
        </div>

        {/* Status Badge */}
        <div className="flex justify-center mb-6">
          <div className="flex flex-col items-center gap-2">
            <RideStatusBadge status={ride.status} />
            {/* WebSocket Connection Status */}
            <div className="flex items-center gap-2 text-xs">
              <div className={`w-2 h-2 rounded-full ${
                connected ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
              }`} />
              <span className="text-text-muted">
                {connected ? 'Live updates' : 'Connecting...'}
              </span>
            </div>
          </div>
        </div>

        {/* Timeline */}
        {ride.status !== 'cancelled' && (
          <Card className="mb-6">
            <RideTimeline currentStatus={ride.status} />
          </Card>
        )}

        {/* Map Placeholder */}
        <Card className="mb-6">
          <MapView
            center={[
              ride.pickup_latitude || 3.8480,
              ride.pickup_longitude || 11.5021
            ]}
            markers={[
              {
                position: [ride.pickup_latitude, ride.pickup_longitude],
                label: 'Pickup',
              },
              {
                position: [ride.dropoff_latitude, ride.dropoff_longitude],
                label: 'Dropoff',
              },
            ]}
            height="300px"
          />
        </Card>

        {/* Driver Card (shown when accepted or started) */}
        {driver && (ride.status === 'accepted' || ride.status === 'started') && (
          <DriverCard driver={driver} eta={eta} className="mb-6" />
        )}

        {/* Ride Details */}
        <Card className="mb-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Ride Details</h3>
          
          <div className="space-y-3">
            {/* Pickup */}
            <div className="flex items-start gap-3">
              <div className="text-primary text-xl">📍</div>
              <div className="flex-1">
                <div className="text-text-muted text-sm">Pickup</div>
                <div className="text-text-primary">{ride.pickup_address || 'Pickup Location'}</div>
              </div>
            </div>

            {/* Dropoff */}
            <div className="flex items-start gap-3">
              <div className="text-secondary text-xl">🎯</div>
              <div className="flex-1">
                <div className="text-text-muted text-sm">Dropoff</div>
                <div className="text-text-primary">{ride.dropoff_address || 'Dropoff Location'}</div>
              </div>
            </div>

            {/* Distance & Fare */}
            <div className="flex items-center justify-between pt-3 border-t border-white/10">
              <div>
                <div className="text-text-muted text-sm">Distance</div>
                <div className="text-text-primary font-semibold">
                  {ride.estimated_distance_km?.toFixed(1)} km
                </div>
              </div>
              <div className="text-right">
                <div className="text-text-muted text-sm">Fare</div>
                <div className="text-primary font-bold text-xl">
                  {Math.round(ride.estimated_fare || ride.offered_fare || 0).toLocaleString()} XAF
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Status Messages */}
        {ride.status === 'requested' && (
          <Card className="mb-6 bg-yellow-500/10 border-yellow-500/50">
            <div className="flex items-center gap-3">
              <div className="text-4xl">🔍</div>
              <div>
                <div className="text-text-primary font-semibold">Finding nearby drivers...</div>
                <div className="text-text-secondary text-sm">This usually takes 1-3 minutes</div>
              </div>
            </div>
          </Card>
        )}

        {ride.status === 'started' && (
          <Card className="mb-6 bg-blue-500/10 border-blue-500/50">
            <div className="flex items-center gap-3">
              <div className="text-4xl">🚗</div>
              <div>
                <div className="text-text-primary font-semibold">On the way to destination</div>
                <div className="text-text-secondary text-sm">
                  {eta ? `Estimated arrival in ${eta} minutes` : 'Calculating ETA...'}
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Cancel Button (only for requested or accepted status) */}
        {(ride.status === 'requested' || ride.status === 'accepted') && (
          <Button
            variant="outline"
            size="lg"
            className="w-full border-red-500/50 text-red-500 hover:bg-red-500/10"
            onClick={handleCancelRide}
            isLoading={cancelling}
          >
            {cancelling ? 'Cancelling...' : 'Cancel Ride'}
          </Button>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-4 bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-red-500 text-sm">
            {error}
          </div>
        )}
      </div>
    </main>
  );
}
