import { Platform } from 'react-native';

// Use explicit LAN IP for testing on physical device on same network
const localhost = '192.168.1.5';

export const API_URL = process.env.EXPO_PUBLIC_API_URL || `http://${localhost}:8000/api/v1`;
export const WS_URL = process.env.EXPO_PUBLIC_WS_URL || `ws://${localhost}:8000/api/v1/ws/connect`;
