/**
 * Custom hook for geolocation
 */

import { useState, useEffect, useCallback } from 'react';
import { geolocationService, Coordinates, LocationResult } from '@/services/geolocation';

export function useGeolocation() {
  const [location, setLocation] = useState<Coordinates | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const getCurrentLocation = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await geolocationService.getCurrentLocation();
      setLocation(result.coords);
    } catch (err: any) {
      setError(err.message);
      // Set default location (Yaoundé) on error
      setLocation(geolocationService.getDefaultLocation());
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    location,
    error,
    loading,
    getCurrentLocation,
  };
}

export function useLocationWatch() {
  const [location, setLocation] = useState<Coordinates | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [watchId, setWatchId] = useState<number | null>(null);

  const startWatching = useCallback(() => {
    const id = geolocationService.watchLocation(
      (result: LocationResult) => {
        setLocation(result.coords);
        setError(null);
      },
      (err: Error) => {
        setError(err.message);
      }
    );
    setWatchId(id);
  }, []);

  const stopWatching = useCallback(() => {
    if (watchId !== null) {
      geolocationService.clearWatch(watchId);
      setWatchId(null);
    }
  }, [watchId]);

  useEffect(() => {
    return () => {
      stopWatching();
    };
  }, [stopWatching]);

  return {
    location,
    error,
    isWatching: watchId !== null,
    startWatching,
    stopWatching,
  };
}
