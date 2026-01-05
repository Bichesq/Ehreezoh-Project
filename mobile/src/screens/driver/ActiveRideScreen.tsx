import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, Dimensions, Platform, Linking } from 'react-native';
import MapView, { Marker, Polyline, PROVIDER_GOOGLE } from 'react-native-maps';
import { StatusBar } from 'expo-status-bar';
import { driverService } from '../../services/driver';
import { Coordinates } from '../../services/location';

// Screen Dimensions
const { width, height } = Dimensions.get('window');

interface ActiveRideScreenProps {
  ride: any; // Replace with proper Ride interface
  currentLocation: Coordinates | null;
  onRideComplete: () => void;
}

export default function ActiveRideScreen({ ride, currentLocation, onRideComplete }: ActiveRideScreenProps) {
  const [status, setStatus] = useState<'accepted' | 'started' | 'completed'>(ride.status);
  const [loading, setLoading] = useState(false);
  const [region, setRegion] = useState({
    latitude: ride.pickup_latitude,
    longitude: ride.pickup_longitude,
    latitudeDelta: 0.02,
    longitudeDelta: 0.02,
  });

  // Effect to update region based on status (Pickup vs Dropoff focus)
  useEffect(() => {
    if (status === 'accepted') {
      // Focus on pickup
      setRegion({
        latitude: ride.pickup_latitude,
        longitude: ride.pickup_longitude,
        latitudeDelta: 0.02,
        longitudeDelta: 0.02,
      });
    } else if (status === 'started') {
      // Focus on dropoff
      setRegion({
        latitude: ride.dropoff_latitude,
        longitude: ride.dropoff_longitude,
        latitudeDelta: 0.05,
        longitudeDelta: 0.05,
      });
    }
  }, [status]);

  const handleNavigate = () => {
    const lat = status === 'accepted' ? ride.pickup_latitude : ride.dropoff_latitude;
    const lng = status === 'accepted' ? ride.pickup_longitude : ride.dropoff_longitude;
    const label = status === 'accepted' ? 'Pickup Location' : 'Dropoff Location';
    
    const scheme = Platform.select({ ios: 'maps:0,0?q=', android: 'geo:0,0?q=' });
    const latLng = `${lat},${lng}`;
    const url = Platform.select({
      ios: `${scheme}${label}@${latLng}`,
      android: `${scheme}${latLng}(${label})`
    });

    if (url) Linking.openURL(url);
  };

  const handleCallPassenger = () => {
    // In a real app, this would use the passenger's phone number
    // We might need to fetch it or have it in the ride object (privacy masking usually)
    Alert.alert('Call Passenger', 'Calling passenger is not implemented in demo.');
  };

  const handleStartRide = async () => {
    setLoading(true);
    try {
      const updatedRide = await driverService.startRide(ride.id);
      setStatus('started');
      Alert.alert('Ride Started', 'Head to the destination.');
    } catch (error) {
      console.error('Start ride error:', error);
      Alert.alert('Error', 'Failed to start ride.');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteRide = async () => {
    setLoading(true);
    try {
      const updatedRide = await driverService.completeRide(ride.id);
      setStatus('completed');
      Alert.alert('Ride Completed', `Fare: ${updatedRide.final_fare || updatedRide.estimated_fare} XAF`);
      onRideComplete();
    } catch (error) {
      console.error('Complete ride error:', error);
      Alert.alert('Error', 'Failed to complete ride.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
import { COLORS } from '../../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../../constants/theme';
import { DARK_MAP_STYLE } from '../../constants/mapStyle';

// ... (imports remain)
      <StatusBar style="light" />
      
      {/* MAP */}
      <MapView
        provider={PROVIDER_GOOGLE}
        style={styles.map}
        customMapStyle={DARK_MAP_STYLE}
        initialRegion={region}
        region={currentLocation ? undefined : region} 
        showsUserLocation
        followsUserLocation={true}
      >
        {/* Pickup Marker */}
        <Marker
            coordinate={{ latitude: ride.pickup_latitude, longitude: ride.pickup_longitude }}
            title="Pickup"
            description={ride.pickup_address}
            pinColor={COLORS.primary}
        />

        {/* Dropoff Marker */}
        <Marker
            coordinate={{ latitude: ride.dropoff_latitude, longitude: ride.dropoff_longitude }}
            title="Dropoff"
            description={ride.dropoff_address}
            pinColor={COLORS.accent}
        />

        {/* Route Line */}
        <Polyline
            coordinates={[
                { latitude: ride.pickup_latitude, longitude: ride.pickup_longitude },
                { latitude: ride.dropoff_latitude, longitude: ride.dropoff_longitude }
            ]}
            strokeColor={COLORS.primary}
            strokeWidth={4}
            lineDashPattern={[10, 10]} 
        />
      </MapView>

      {/* Bottom Action Sheet */}
      <View style={styles.bottomSheet}>
        {/* Header: Passenger & Status */}
        <View style={styles.header}>
            <View>
                <Text style={styles.passengerName}>Passenger (Rating: 4.8★)</Text> 
                <Text style={styles.rideStatus}>
                    {status === 'accepted' ? 'Heading to Pickup' : 'Heading to Dropoff'}
                </Text>
            </View>
            <TouchableOpacity style={styles.callButton} onPress={handleCallPassenger}>
                <Text style={styles.callButtonText}>📞 Call</Text>
            </TouchableOpacity>
        </View>

        <View style={styles.divider} />

        {/* Details: Address & Fare */}
        <View style={styles.detailsContainer}>
            <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Dest:</Text>
                <Text style={styles.detailValue} numberOfLines={1}>{
                    status === 'accepted' ? ride.pickup_address : ride.dropoff_address
                }</Text>
            </View>
            <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Fare:</Text>
                <Text style={styles.detailValue}>{ride.estimated_fare?.toLocaleString()} XAF</Text>
            </View>
        </View>

        {/* Actions */}
        <View style={styles.actionsContainer}>
            <TouchableOpacity style={styles.navButton} onPress={handleNavigate}>
                <Text style={styles.navButtonText}>Navigate</Text>
            </TouchableOpacity>

            {status === 'accepted' ? (
                <TouchableOpacity 
                    style={[styles.mainActionButton, styles.startButton]} 
                    onPress={handleStartRide}
                    disabled={loading}
                >
                    <Text style={styles.mainActionText}>
                        {loading ? 'Starting...' : 'SLIDE TO START'}
                    </Text>
                </TouchableOpacity>
            ) : (
                <TouchableOpacity 
                    style={[styles.mainActionButton, styles.completeButton]} 
                    onPress={handleCompleteRide}
                    disabled={loading}
                >
                    <Text style={styles.mainActionText}>
                        {loading ? 'Completing...' : 'SLIDE TO COMPLETE'}
                    </Text>
                </TouchableOpacity>
            )}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  map: {
    width: width,
    height: height, 
  },
  bottomSheet: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: COLORS.card,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: 40,
    ...SHADOWS.medium,
    borderTopWidth: 1,
    borderColor: COLORS.primary,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  passengerName: {
    ...TYPOGRAPHY.subheader,
    color: COLORS.text,
  },
  rideStatus: {
    fontSize: 14,
    color: COLORS.primary,
    fontWeight: 'bold',
    marginTop: 4,
  },
  callButton: {
    backgroundColor: COLORS.background,
    padding: 12,
    borderRadius: 50,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  callButtonText: {
    fontSize: 16,
    color: COLORS.text,
  },
  divider: {
    height: 1,
    backgroundColor: COLORS.border,
    marginBottom: 20,
  },
  detailsContainer: {
    marginBottom: 24,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  detailLabel: {
    fontSize: 16,
    color: COLORS.textDim,
    width: 60,
  },
  detailValue: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    flex: 1,
  },
  actionsContainer: {
    flexDirection: 'row',
    gap: 16,
  },
  navButton: {
    backgroundColor: COLORS.secondary,
    padding: 16,
    borderRadius: 12,
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  navButtonText: {
    color: COLORS.background,
    fontWeight: 'bold',
    fontSize: 16,
  },
  mainActionButton: {
    padding: 16,
    borderRadius: 12,
    flex: 2,
    alignItems: 'center',
    justifyContent: 'center',
    ...SHADOWS.neon,
  },
  startButton: {
    backgroundColor: COLORS.primary,
  },
  completeButton: {
    backgroundColor: COLORS.accent,
  },
  mainActionText: {
    color: COLORS.background,
    fontWeight: 'bold',
    fontSize: 16,
    letterSpacing: 1,
  },
});
