import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Animated, DeviceEventEmitter } from 'react-native';
import NetInfo from '@react-native-community/netinfo';
import { COLORS } from '../constants/colors';
import { SHADOWS } from '../constants/theme';

export default function NetworkErrorBanner() {
  const [status, setStatus] = useState<'NONE' | 'RETRYING' | 'ERROR'>('NONE');
  const [retryCount, setRetryCount] = useState(0);
  const translateY = new Animated.Value(-100);

  useEffect(() => {
    // Check initial state
    NetInfo.fetch().then(state => {
         if (state.isConnected === false) {
             setStatus('ERROR');
             showBanner();
         }
    });

    const showBanner = () => {
      Animated.timing(translateY, {
        toValue: 0,
        useNativeDriver: true,
        duration: 300,
      }).start();
    };

    const hideBanner = () => {
      Animated.timing(translateY, {
        toValue: -100,
        useNativeDriver: true,
        duration: 300,
      }).start(() => setStatus('NONE'));
    };

    // Event Listeners
    const retrySub = DeviceEventEmitter.addListener('network_retry', ({ count }) => {
      setStatus('RETRYING');
      setRetryCount(count);
      showBanner();
    });

    const errorSub = DeviceEventEmitter.addListener('network_error', () => {
      setStatus('ERROR');
      showBanner();
    });

    const connectedSub = DeviceEventEmitter.addListener('network_connected', () => {
      if (status !== 'NONE') {
        hideBanner();
      }
    });
    
    // NetInfo Listener
    const unsubscribeNet = NetInfo.addEventListener(state => {
        if (state.isConnected === false) {
            setStatus('ERROR');
            showBanner();
        } else if (state.isConnected && state.isInternetReachable) {
            // Only hide if we were in error state
            if (status === 'ERROR') hideBanner();
        }
    });

    return () => {
      retrySub.remove();
      errorSub.remove();
      connectedSub.remove();
      unsubscribeNet();
    };
  }, [status]);

  if (status === 'NONE') return null;

  return (
    <Animated.View style={[
        styles.container, 
        { transform: [{ translateY }] },
        status === 'ERROR' ? styles.errorBg : styles.retryBg
    ]}>
      <Text style={styles.text}>
        {status === 'ERROR' 
            ? '⚠️ No Internet Connection' 
            : `🔄 Connecting... (Attempt ${retryCount})`}
      </Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 50, // Below notch
    left: 20,
    right: 20,
    padding: 12,
    borderRadius: 8,
    zIndex: 9999,
    alignItems: 'center',
    ...SHADOWS.medium,
  },
  errorBg: {
    backgroundColor: COLORS.danger,
  },
  retryBg: {
    backgroundColor: COLORS.accent,
  },
  text: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  }
});
