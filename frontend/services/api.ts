/**
 * Ehreezoh API Service
 * Centralized API client for backend communication
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Types
export interface RideRequest {
  ride_type: 'moto' | 'car';
  pickup_latitude: number;
  pickup_longitude: number;
  pickup_address?: string;
  dropoff_latitude: number;
  dropoff_longitude: number;
  dropoff_address?: string;
  offered_fare?: number;
}

export interface DriverRegistration {
  driver_license_number: string;
  vehicle_type: 'moto' | 'car';
  vehicle_plate_number: string;
  vehicle_make?: string;
  vehicle_model?: string;
  vehicle_year?: number;
  vehicle_color?: string;
}

export interface LocationUpdate {
  latitude: number;
  longitude: number;
}

export interface DriverStatusUpdate {
  is_online?: boolean;
  is_available?: boolean;
}

// API Service
export const api = {
  // ===== DRIVER APIs =====
  driver: {
    /**
     * Register current user as a driver
     */
    register: (data: DriverRegistration) => 
      apiClient.post('/drivers/register', data),

    /**
     * Get current driver's profile
     */
    getProfile: () => 
      apiClient.get('/drivers/me'),

    /**
     * Update driver online/available status
     */
    updateStatus: (data: DriverStatusUpdate) => 
      apiClient.patch('/drivers/status', data),

    /**
     * Update driver's current location
     */
    updateLocation: (data: LocationUpdate) => 
      apiClient.post('/drivers/location', data),

    /**
     * Find nearby drivers
     */
    getNearby: (params: {
      latitude: number;
      longitude: number;
      radius_km?: number;
      vehicle_type?: 'moto' | 'car';
      limit?: number;
    }) => 
      apiClient.get('/drivers/nearby', { params }),
  },

  // ===== RIDE APIs =====
  rides: {
    /**
     * Request a new ride
     */
    request: (data: RideRequest) => 
      apiClient.post('/rides/request', data),

    /**
     * Get ride details by ID
     */
    get: (rideId: string) => 
      apiClient.get(`/rides/${rideId}`),

    /**
     * Driver accepts a ride
     */
    accept: (rideId: string) => 
      apiClient.patch(`/rides/${rideId}/accept`),

    /**
     * Driver starts a ride
     */
    start: (rideId: string) => 
      apiClient.patch(`/rides/${rideId}/start`),

    /**
     * Driver completes a ride
     */
    complete: (rideId: string, finalFare?: number) => 
      apiClient.patch(`/rides/${rideId}/complete`, null, {
        params: { final_fare: finalFare }
      }),

    /**
     * Cancel a ride
     */
    cancel: (rideId: string, reason?: string) => 
      apiClient.patch(`/rides/${rideId}/cancel`, { reason }),

    /**
     * Get ride history
     */
    getHistory: (params?: {
      status?: string;
      limit?: number;
    }) => 
      apiClient.get('/rides', { params }),
  },

  // ===== USER APIs =====
  user: {
    /**
     * Get current user profile
     */
    getProfile: () => 
      apiClient.get('/auth/me'),

    /**
     * Update user profile
     */
    updateProfile: (data: {
      full_name?: string;
      email?: string;
      language_preference?: 'fr' | 'en';
    }) => 
      apiClient.patch('/auth/me', data),
  },

  // ===== HEALTH CHECK =====
  health: {
    /**
     * Check API health
     */
    check: () => 
      apiClient.get('/health'),
  },
};

// Helper function to handle API errors
export function getErrorMessage(error: any): string {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
}

export default api;
