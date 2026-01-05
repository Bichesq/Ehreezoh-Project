import axios, { AxiosError } from 'axios';
import axiosRetry from 'axios-retry';
import * as SecureStore from 'expo-secure-store';
import NetInfo from '@react-native-community/netinfo';
import { API_URL } from '../config';
import { DeviceEventEmitter } from 'react-native';

const TOKEN_KEY = 'auth_token';

// Create Axios Instance
export const api = axios.create({
  baseURL: API_URL,
  timeout: 10000, // 10s timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Monitor Network State
NetInfo.addEventListener(state => {
    if (state.isConnected && state.isInternetReachable) {
        DeviceEventEmitter.emit('network_connected');
    } else if (state.isConnected === false) {
        DeviceEventEmitter.emit('network_error');
    }
});

// Configure Retry Logic
axiosRetry(api, {
  retries: 3,
  retryDelay: (retryCount: number) => {
    // Exponential backoff: 1s, 2s, 4s
    return retryCount * 1000; 
  },
  retryCondition: (error: AxiosError) => {
    // Retry on network errors or 5xx status codes
    return axiosRetry.isNetworkOrIdempotentRequestError(error) || (error.response?.status ? error.response.status >= 500 : false);
  },
  onRetry: (retryCount: number, error: AxiosError, requestConfig: any) => {
    console.log(`[API] Retrying request... Attempt ${retryCount}`);
    DeviceEventEmitter.emit('network_retry', { count: retryCount });
  }
});

// Request Interceptor: Attach Token & Check Network
api.interceptors.request.use(
  async (config) => {
    // Optional: Fail fast if definitely offline (improves UX)
    const netState = await NetInfo.fetch();
    if (config.method !== 'get' && netState.isConnected === false) {
        // For GET requests we might want to let them fail to trigger cache fallback
        // For POST/PUT related to business logic, we might want to queue them, but here we just proceed and let axios fail if needed
    }

    try {
      const token = await SecureStore.getItemAsync(TOKEN_KEY);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error attaching token:', error);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Error Handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.message === 'Network Error' || !error.response) {
       console.log('[API] Network Error Detected');
       DeviceEventEmitter.emit('network_error');
    }
    
    // Handle 401 Unauthorized globally
    if (error.response?.status === 401) {
       // Could emit 'logout' event here
    }

    return Promise.reject(error);
  }
);

