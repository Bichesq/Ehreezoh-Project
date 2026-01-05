import { api } from './api';
import { socketService } from './socket';

export const driverService = {
  // Toggle Online Status via WebSocket (updates DB & Redis on backend)
  goOnline: () => {
    socketService.send('driver_online');
  },

  goOffline: () => {
    socketService.send('driver_offline');
  },

  // Accept a ride offer
  acceptRide: async (rideId: string) => {
    const response = await api.patch(`/rides/${rideId}/accept`);
    return response.data;
  },

  // Start a ride (passenger picked up)
  startRide: async (rideId: string) => {
    const response = await api.patch(`/rides/${rideId}/start`);
    return response.data;
  },

  // Complete a ride (passenger dropped off)
  completeRide: async (rideId: string) => {
    const response = await api.patch(`/rides/${rideId}/complete`);
    return response.data;
  },

  // Cancel a ride (e.g., passenger no-show)
  cancelRide: async (rideId: string, reason: string) => {
    const response = await api.patch(`/rides/${rideId}/cancel`, {
      reason
    });
    return response.data;
  }
};
