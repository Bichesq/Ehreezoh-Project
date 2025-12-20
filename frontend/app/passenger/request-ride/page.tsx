/**
 * Request Ride Page
 * Passenger interface for requesting a ride
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button, Input, Card } from '@/components/ui';
import { RideTypeSelector } from '@/components/Ride/RideTypeSelector';
import { FareEstimate } from '@/components/Ride/FareEstimate';
import { useGeolocation } from '@/hooks/useGeolocation';
import { api, getErrorMessage } from '@/services/api';
import { geolocationService } from '@/services/geolocation';

export default function RequestRidePage() {
  const router = useRouter();
  const { location: currentLocation, getCurrentLocation, loading: locationLoading } = useGeolocation();

  const [rideType, setRideType] = useState<'moto' | 'car'>('moto');
  const [pickupAddress, setPickupAddress] = useState('');
  const [dropoffAddress, setDropoffAddress] = useState('');
  const [pickupCoords, setPickupCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [dropoffCoords, setDropoffCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [distance, setDistance] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Get current location on mount
  useEffect(() => {
    getCurrentLocation();
  }, [getCurrentLocation]);

  // Set pickup to current location when available
  useEffect(() => {
    if (currentLocation && !pickupCoords) {
      setPickupCoords({
        lat: currentLocation.latitude,
        lng: currentLocation.longitude,
      });
      setPickupAddress('Current Location');
    }
  }, [currentLocation, pickupCoords]);

  // Calculate distance when both coordinates are set
  useEffect(() => {
    if (pickupCoords && dropoffCoords) {
      const dist = geolocationService.calculateDistance(
        { latitude: pickupCoords.lat, longitude: pickupCoords.lng },
        { latitude: dropoffCoords.lat, longitude: dropoffCoords.lng }
      );
      setDistance(dist);
    } else {
      setDistance(null);
    }
  }, [pickupCoords, dropoffCoords]);

  const handleUseCurrentLocation = async () => {
    await getCurrentLocation();
  };

  // Temporary: Set dropoff coordinates manually
  // TODO: Replace with map picker
  const handleSetDropoff = () => {
    // Example: Set to a location 5km away from pickup
    if (pickupCoords) {
      setDropoffCoords({
        lat: pickupCoords.lat + 0.045, // ~5km north
        lng: pickupCoords.lng + 0.045, // ~5km east
      });
      setDropoffAddress('Destination (5km away)');
    }
  };

  const handleRequestRide = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!pickupCoords || !dropoffCoords) {
      setError('Please set both pickup and dropoff locations');
      return;
    }

    setIsLoading(true);

    try {
      const response = await api.rides.request({
        ride_type: rideType,
        pickup_latitude: pickupCoords.lat,
        pickup_longitude: pickupCoords.lng,
        pickup_address: pickupAddress,
        dropoff_latitude: dropoffCoords.lat,
        dropoff_longitude: dropoffCoords.lng,
        dropoff_address: dropoffAddress,
      });

      // Redirect to ride tracking page
      router.push(`/passenger/ride/${response.data.id}`);
    } catch (err: any) {
      console.error('Ride request error:', err);
      console.error('Error response:', err.response);
      console.error('Token in localStorage:', localStorage.getItem('access_token'));
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

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
          <h1 className="text-2xl font-bold text-text-primary">Request Ride</h1>
          <div className="w-16"></div> {/* Spacer for centering */}
        </div>

        <form onSubmit={handleRequestRide} className="space-y-6">
          {/* Map Placeholder */}
          <Card>
            <div className="bg-bg-secondary rounded-lg h-64 flex items-center justify-center border border-white/10">
              <div className="text-center">
                <div className="text-4xl mb-2">🗺️</div>
                <div className="text-text-secondary">Map will appear here</div>
                <div className="text-sm text-text-muted mt-1">
                  {pickupCoords && `Pickup: ${pickupCoords.lat.toFixed(4)}, ${pickupCoords.lng.toFixed(4)}`}
                </div>
                <div className="text-sm text-text-muted">
                  {dropoffCoords && `Dropoff: ${dropoffCoords.lat.toFixed(4)}, ${dropoffCoords.lng.toFixed(4)}`}
                </div>
              </div>
            </div>
          </Card>

          {/* Pickup Location */}
          <Card>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-text-primary font-medium">
                <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Pickup Location
              </div>
              <Input
                type="text"
                value={pickupAddress}
                onChange={(e) => setPickupAddress(e.target.value)}
                placeholder="Enter pickup address"
                required
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleUseCurrentLocation}
                isLoading={locationLoading}
                className="w-full"
              >
                📍 Use Current Location
              </Button>
            </div>
          </Card>

          {/* Dropoff Location */}
          <Card>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-text-primary font-medium">
                <svg className="w-5 h-5 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Dropoff Location
              </div>
              <Input
                type="text"
                value={dropoffAddress}
                onChange={(e) => setDropoffAddress(e.target.value)}
                placeholder="Enter destination"
                required
              />
              {/* Temporary button for testing */}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleSetDropoff}
                className="w-full"
              >
                🎯 Set Test Destination (5km away)
              </Button>
            </div>
          </Card>

          {/* Ride Type Selection */}
          <Card>
            <div className="space-y-3">
              <div className="text-text-primary font-medium">Choose Ride Type</div>
              <RideTypeSelector selected={rideType} onChange={setRideType} />
            </div>
          </Card>

          {/* Fare Estimate */}
          {distance && (
            <FareEstimate
              rideType={rideType}
              distance={distance}
            />
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-red-500 text-sm">
              {error}
            </div>
          )}

          {/* Request Button */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full"
            isLoading={isLoading}
            disabled={!pickupCoords || !dropoffCoords}
          >
            {isLoading ? 'Finding Drivers...' : 'Request Ride 🚀'}
          </Button>

          {/* Info */}
          <div className="text-center text-sm text-text-muted">
            <p>We'll match you with nearby drivers</p>
            <p className="mt-1">Average wait time: 2-5 minutes</p>
          </div>
        </form>
      </div>
    </main>
  );
}
