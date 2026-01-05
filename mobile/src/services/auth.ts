import { api } from './api';
import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_data';

export interface User {
  id: string;
  phone_number: string;
  full_name: string;
  is_driver: boolean;
  is_passenger: boolean;
  points: number;
  reputation_score: number;
  trust_score: number;
  total_reports: number;
  total_people_helped: number;
  current_streak: number;
  email?: string;
  profile_photo_url?: string;
}

export const authService = {
  // Login with Phone Number (Mock in Dev)
  login: async (phoneNumber: string) => {
    // In production, get ID token from Firebase
    // In dev, send "mock_token_" + phoneNumber
    const firebaseToken = `mock_token_${phoneNumber}`;
    
    // api baseURL is already API_URL
    const response = await api.post('/auth/login', {
      firebase_token: firebaseToken
    });
    
    return response.data;
  },

  // Register
  register: async (phoneNumber: string, fullName: string, email: string) => {
    const firebaseToken = `mock_token_${phoneNumber}`;
    
    const response = await api.post('/auth/register', {
      firebase_token: firebaseToken,
      full_name: fullName,
      email: email,
      language_preference: 'en'
    });
    
    return response.data;
  },

  // Storage Utils
  saveToken: async (token: string, user: User) => {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
    await SecureStore.setItemAsync(USER_KEY, JSON.stringify(user));
  },

  getToken: async () => {
    return await SecureStore.getItemAsync(TOKEN_KEY);
  },

  getUser: async () => {
    const user = await SecureStore.getItemAsync(USER_KEY);
    return user ? JSON.parse(user) : null;
  },

  logout: async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(USER_KEY);
  },

  updateProfile: async (data: { full_name?: string; email?: string; language_preference?: string; profile_photo_url?: string }) => {
    const response = await api.patch('/auth/me', data);
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};
