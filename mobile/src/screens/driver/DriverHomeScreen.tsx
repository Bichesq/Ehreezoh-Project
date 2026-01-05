import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, Alert, Dimensions, Switch } from 'react-native';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import { useRouter } from 'expo-router';
import { useSocket } from '../../context/SocketContext';
import { locationService, Coordinates } from '../../services/location';
import { driverService } from '../../services/driver';
import { useAuth } from '../../context/AuthContext';
import { StatusBar } from 'expo-status-bar';
import { COLORS } from '../../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../../constants/theme';
import { DARK_MAP_STYLE } from '../../constants/mapStyle';

export default function DriverHomeScreen() {
  const [location, setLocation] = useState<Coordinates | null>(null);
  const [isOnline, setIsOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const router = useRouter();
  
  const [currentRide, setCurrentRide] = useState<any>(null); // State for active ride
  const [completedRide, setCompletedRide] = useState<any>(null); // Lifted state for rating
  
  const { user } = useAuth();
  const { socket, activeOffer, clearOffer } = useSocket();

  useEffect(() => {
    if (activeOffer) {
      console.log('ACTIVE OFFER RECEIVED:', activeOffer);
    }
  }, [activeOffer]);

  useEffect(() => {
    (async () => {
      const currentLoc = await locationService.getCurrentPosition();
      if (currentLoc) {
        setLocation(currentLoc);
        if (isOnline) {
             socket.send('driver_location_update', currentLoc);
        }
      }
      setLoading(false);

      const sub = await locationService.watchPosition((coords) => {
        setLocation(coords);
        if (isOnline) {
          socket.send('driver_location_update', coords);
        }
      });
      
      return () => sub.remove();
    })();
  }, [isOnline]); 

  const toggleOnline = (value: boolean) => {
    setIsOnline(value);
    if (value) {
      driverService.goOnline();
      Alert.alert('You are Online', 'Waiting for ride requests...');
    } else {
      driverService.goOffline();
      Alert.alert('You are Offline', 'You will not receive new requests.');
    }
  };

  const handleAcceptRide = async () => {
    if (!activeOffer) return;

    setAccepting(true);
    try {
      const ride = await driverService.acceptRide(activeOffer.ride_id);
      setCurrentRide(ride); // This should transition to ActiveRideScreen
      clearOffer(); 
    } catch (error: any) {
      console.error('Accept ride error:', error);
      Alert.alert('Error', 'Failed to accept ride. It may be taken.');
      clearOffer();
    } finally {
      setAccepting(false);
    }
  };

  const handleRideComplete = (ride: any) => {
    setCompletedRide(ride);
    setCurrentRide(null); 
  };

  const handleRatingComplete = () => {
      setCompletedRide(null);
      setIsOnline(true);
      Alert.alert('Available', 'You are now ready to accept new rides.');
  };

  if (loading || !location) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Locating...</Text>
      </View>
    );
  }

  // If there is an active ride, show ActiveRideScreen
  if (currentRide) {
      const ActiveRideScreen = require('./ActiveRideScreen').default;
      return <ActiveRideScreen 
          ride={currentRide} 
          currentLocation={location}
          onRideComplete={handleRideComplete}
      />;
  }

  // If ride completed, show Rating Screen
  if (completedRide) {
      const DriverRatingScreen = require('./DriverRatingScreen').default;
      return <DriverRatingScreen 
          ride={completedRide}
          onComplete={handleRatingComplete}
      />;
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <MapView
        provider={PROVIDER_GOOGLE}
        style={styles.map}
        customMapStyle={DARK_MAP_STYLE}
        initialRegion={{
          latitude: location.latitude,
          longitude: location.longitude,
          latitudeDelta: 0.01,
          longitudeDelta: 0.01,
        }}
        showsUserLocation
        followsUserLocation
      />

      {/* Top Status Card */}
      <View style={styles.topContainer}>
          <View style={[styles.statusCard, isOnline ? styles.statusOnline : styles.statusOffline]}>
            <View style={styles.statusRow}>
                <View>
                    <Text style={styles.greeting}>Driver: {user?.full_name}</Text>
                    <Text style={styles.statusSubtext}>
                         {isOnline ? '● You are Online' : '○ You are Offline'}
                    </Text>
                </View>
                <Switch 
                    value={isOnline} 
                    onValueChange={toggleOnline}
                    trackColor={{ false: COLORS.customGray || "#767577", true: COLORS.primary }}
                    thumbColor="#f4f3f4"
                />
            </View>
          </View>
          
          <TouchableOpacity onPress={() => router.push('/history')} style={styles.historyLink}>
             <Text style={styles.historyLinkText}>View Ride History</Text>
          </TouchableOpacity>
      </View>

      {/* Ride Offer Alert Overlay */}
      {activeOffer && (
        <View style={styles.overlayContainer}>
            <View style={styles.offerCard}>
                <View style={styles.pulseIndicator} />
                <Text style={styles.offerTitle}>🎉 New Ride Request!</Text>
                
                <View style={styles.offerDetails}>
                    <Text style={styles.offerFare}>{activeOffer.estimated_fare.toLocaleString()} XAF</Text>
                    <Text style={styles.offerDistance}>{activeOffer.distance_km.toFixed(1)} km pickup</Text>
                </View>

                <View style={styles.addressContainer}>
                    <Text style={styles.label}>PICKUP LOCATION</Text>
                    <Text style={styles.address}>{activeOffer.pickup_address}</Text>
                </View>

                <TouchableOpacity 
                    style={styles.acceptButton}
                    onPress={handleAcceptRide}
                    disabled={accepting}
                >
                    <Text style={styles.acceptButtonText}>
                        {accepting ? 'Accepting...' : 'ACCEPT RIDE'}
                    </Text>
                </TouchableOpacity>
                
                <TouchableOpacity 
                    style={styles.declineButton}
                    onPress={clearOffer}
                >
                    <Text style={styles.declineButtonText}>Decline</Text>
                </TouchableOpacity>
            </View>
        </View>
      )}


    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  loadingText: {
      color: COLORS.text,
  },
  map: {
    width: Dimensions.get('window').width,
    height: Dimensions.get('window').height,
  },
  topContainer: {
      position: 'absolute',
      top: 160, // Pushed down to clear Role Toggle
      left: 20,
      right: 20,
  },
  statusCard: {
    backgroundColor: COLORS.card,
    padding: 20,
    borderRadius: 16,
    ...SHADOWS.medium,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  statusOnline: {
      borderColor: COLORS.primary,
      borderWidth: 2,
  },
  statusOffline: {
      borderColor: COLORS.border,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  greeting: {
    ...TYPOGRAPHY.subheader,
    color: COLORS.text,
  },
  statusSubtext: {
      ...TYPOGRAPHY.caption,
      marginTop: 4,
      color: COLORS.textDim,
  },
  historyLink: {
    marginTop: 15,
    alignSelf: 'center',
    backgroundColor: 'rgba(30, 41, 59, 0.8)',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
  },
  historyLinkText: {
    color: COLORS.primary,
    fontWeight: '600',
  },
  
  // Offer Card
  overlayContainer: {
      ...StyleSheet.absoluteFillObject,
      backgroundColor: 'rgba(0,0,0,0.6)',
      justifyContent: 'flex-end',
      zIndex: 100,
  },
  offerCard: {
    backgroundColor: COLORS.card,
    padding: 24,
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    ...SHADOWS.neon,
    borderTopWidth: 2,
    borderTopColor: COLORS.primary,
  },
  pulseIndicator: {
      width: 60,
      height: 6,
      backgroundColor: COLORS.primary,
      borderRadius: 3,
      alignSelf: 'center',
      marginBottom: 20,
      opacity: 0.5,
  },
  offerTitle: {
    color: COLORS.primary,
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
  },
  offerDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: 15,
    borderRadius: 12,
  },
  offerFare: {
    color: COLORS.text,
    fontSize: 32,
    fontWeight: 'bold',
  },
  offerDistance: {
    color: COLORS.textDim,
    fontSize: 16,
  },
  addressContainer: {
    marginBottom: 30,
  },
  label: {
    color: COLORS.textDim,
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 8,
  },
  address: {
    color: COLORS.text,
    fontSize: 18,
    fontWeight: '500',
  },
  acceptButton: {
    backgroundColor: COLORS.primary,
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
    marginBottom: 12,
    ...SHADOWS.neon,
  },
  acceptButtonText: {
    color: COLORS.background,
    fontSize: 20,
    fontWeight: 'bold',
  },
  declineButton: {
    padding: 16,
    alignItems: 'center',
  },
  declineButtonText: {
    color: COLORS.danger,
    fontSize: 16,
    fontWeight: '600',
  },
});
