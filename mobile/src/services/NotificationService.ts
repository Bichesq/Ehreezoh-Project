import { Platform } from 'react-native';
import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';

// Configure how notifications behave when app is in foreground
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export const notificationService = {
  registerForPushNotificationsAsync: async (): Promise<string | undefined> => {
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });
    }

    if (!Device.isDevice) {
      console.log('Must use physical device for Push Notifications');
      // For development in simulator, return a mock token or undefined?
      // return undefined;
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      console.log('Failed to get push token for push notification!');
      return undefined;
    }

    try {
      const projectId =
        Constants?.expoConfig?.extra?.eas?.projectId ?? Constants?.easConfig?.projectId;
        
      if (!projectId) {
         // Fallback or just let getExpoPushTokenAsync handle it if configured in app.json
         console.log("Project ID not found in Constants, trying default...");
      }

      const tokenData = await Notifications.getExpoPushTokenAsync({
        projectId: projectId, // Optional, depending on config
      });
      console.log('Expo Push Token:', tokenData.data);
      return tokenData.data;
    } catch (e: any) {
      console.error('Error getting push token:', e);
      return undefined;
    }
  },

  addNotificationListener: (callback: (notification: Notifications.Notification) => void) => {
    return Notifications.addNotificationReceivedListener(callback);
  },

  addResponseReceivedListener: (callback: (response: Notifications.NotificationResponse) => void) => {
    return Notifications.addNotificationResponseReceivedListener(callback);
  },
  
  removeNotificationSubscription: (subscription: Notifications.Subscription) => {
    subscription.remove();
  }
};
