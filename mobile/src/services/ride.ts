import { api } from './api';

export interface RideRequest {
  ride_type: 'moto' | 'car';
  pickup_latitude: number;
  pickup_longitude: number;
  dropoff_latitude: number;
  dropoff_longitude: number;
  pickup_address: string;
  dropoff_address?: string; // Optional for now (hail anywhere)
}

export interface Ride {
  id: string;
  status: string;
  driver_id?: string;
  estimated_fare: number;
  driver_location?: { latitude: number; longitude: number };
}

export const rideService = {
  requestRide: async (request: RideRequest): Promise<Ride> => {
    const response = await api.post('/rides/request', request);
    return response.data;
  },

  cancelRide: async (rideId: string) => {
    const response = await api.patch(`/rides/${rideId}/cancel`, { reason: 'User cancelled' });
    return response.data;
  },

  rateRide: async (rideId: string, rating: number, review?: string) => {
    const response = await api.post(`/rides/${rideId}/rate`, { rating, review });
    return response.data;
  },

  getRides: async (status?: string, limit: number = 20) => {
    const params: any = { limit };
    if (status) params.status = status;
    const response = await api.get('/rides/', { params });
    return response.data;
  },

  initiatePayment: async (rideId: string, provider: string, phone_number: string) => {
    const response = await api.post(`/rides/${rideId}/pay`, { provider, phone_number });
    return response.data;
  },

  getRide: async (rideId: string) => {
      const response = await api.get(`/rides/${rideId}`);
      return response.data;
  }
};
