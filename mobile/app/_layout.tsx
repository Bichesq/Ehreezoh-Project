import { Stack } from 'expo-router';
import { AuthProvider } from '../src/context/AuthContext';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { SocketProvider } from '../src/context/SocketContext';
import NetworkErrorBanner from '../src/components/NetworkErrorBanner';
import { useEffect, useRef } from 'react';
import NetInfo from '@react-native-community/netinfo';
import { incidentService } from '../src/services/incident';
import { notificationService } from '../src/services/NotificationService';
import * as Notifications from 'expo-notifications';

export default function RootLayout() {
  const notificationListener = useRef<Notifications.Subscription>();
  const responseListener = useRef<Notifications.Subscription>();

  useEffect(() => {
    // 1. Offline Sync Listener
    const unsubscribeNet = NetInfo.addEventListener(state => {
      if (state.isConnected && state.isInternetReachable) {
        console.log('[Network] Online - attempting to sync offline reports...');
        incidentService.syncOfflineReports();
      }
    });

    // 2. Push Notification Setup
    notificationService.registerForPushNotificationsAsync().then(token => {
      if (token) {
        // TODO: Send token to backend (user service) once we have the user object available or in AuthContext
        console.log('Device Push Token:', token);
      }
    });

    notificationListener.current = notificationService.addNotificationListener(notification => {
      console.log('Notification Received (Foreground):', notification);
    });

    responseListener.current = notificationService.addResponseReceivedListener(response => {
      console.log('Notification Tapped:', response);
      // Determine navigation here based on response.notification.request.content.data
    });

    return () => {
      unsubscribeNet();
      if (notificationListener.current) notificationService.removeNotificationSubscription(notificationListener.current);
      if (responseListener.current) notificationService.removeNotificationSubscription(responseListener.current);
    };
  }, []);

  return (
    <SafeAreaProvider>
        <NetworkErrorBanner />
        <AuthProvider>
          <SocketProvider>
            <Stack>
                <Stack.Screen name="(auth)/login" options={{ headerShown: false }} />
                <Stack.Screen name="(auth)/register" options={{ headerShown: false }} />
                <Stack.Screen name="index" options={{ headerShown: false }} />
                <Stack.Screen name="report/index" options={{ 
                    headerShown: false,
                    presentation: 'modal',
                    animation: 'slide_from_bottom'
                }} />
                {/* Community screens */}
                <Stack.Screen name="community/chat/index" options={{ headerShown: false }} />
                <Stack.Screen name="community/chat/[roomId]" options={{ headerShown: false }} />
            </Stack>
          </SocketProvider>
        </AuthProvider>
    </SafeAreaProvider>
  );
}
