/**
 * useRideWebSocket Hook
 * Real-time ride updates via WebSocket
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { wsService } from '@/services/websocket';

interface RideUpdate {
  status?: string;
  driver?: any;
  location?: {
    latitude: number;
    longitude: number;
  };
  eta?: number;
}

export function useRideWebSocket(rideId: string | null) {
  const [connected, setConnected] = useState(false);
  const [rideUpdate, setRideUpdate] = useState<RideUpdate | null>(null);

  useEffect(() => {
    if (!rideId) return;

    // Get user ID and token from localStorage
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('user');
    
    if (!token || !userStr) {
      console.warn('⚠️ No auth token or user found');
      return;
    }

    const user = JSON.parse(userStr);
    const userId = user.id;

    // Event handlers
    const handleConnected = () => {
      console.log('✅ WebSocket connected');
      setConnected(true);
      // Subscribe to ride updates after connection is established
      wsService.subscribeToRide(rideId);
    };

    const handleDisconnected = () => {
      console.log('🔌 WebSocket disconnected');
      setConnected(false);
    };

    const handleRideAccepted = (data: any) => {
      console.log('🚗 Ride accepted:', data);
      setRideUpdate({
        status: 'accepted',
        driver: data.driver,
      });
    };

    const handleRideStarted = (data: any) => {
      console.log('🚀 Ride started:', data);
      setRideUpdate({
        status: 'started',
      });
    };

    const handleRideCompleted = (data: any) => {
      console.log('🎉 Ride completed:', data);
      setRideUpdate({
        status: 'completed',
      });
    };

    const handleRideCancelled = (data: any) => {
      console.log('❌ Ride cancelled:', data);
      setRideUpdate({
        status: 'cancelled',
      });
    };

    const handleDriverLocationUpdate = (data: any) => {
      console.log('📍 Driver location update:', data);
      setRideUpdate({
        location: data.location,
        eta: data.eta,
      });
    };

    // Register event listeners BEFORE connecting
    wsService.on('connected', handleConnected);
    wsService.on('disconnected', handleDisconnected);
    wsService.on('ride_accepted', handleRideAccepted);
    wsService.on('ride_started', handleRideStarted);
    wsService.on('ride_completed', handleRideCompleted);
    wsService.on('ride_cancelled', handleRideCancelled);
    wsService.on('driver_location_update', handleDriverLocationUpdate);

    // Connect to WebSocket AFTER registering handlers
    if (!wsService.isConnected()) {
      wsService.connect(userId, token);
    } else {
      // Already connected, just subscribe
      wsService.subscribeToRide(rideId);
    }

    // Cleanup
    return () => {
      wsService.off('connected', handleConnected);
      wsService.off('disconnected', handleDisconnected);
      wsService.off('ride_accepted', handleRideAccepted);
      wsService.off('ride_started', handleRideStarted);
      wsService.off('ride_completed', handleRideCompleted);
      wsService.off('ride_cancelled', handleRideCancelled);
      wsService.off('driver_location_update', handleDriverLocationUpdate);
      
      if (rideId) {
        wsService.unsubscribeFromRide(rideId);
      }
    };
  }, [rideId]);

  return {
    connected,
    rideUpdate,
  };
}

export default useRideWebSocket;
