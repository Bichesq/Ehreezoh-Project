import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Dimensions, ActivityIndicator } from 'react-native';
import { COLORS } from '../../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../../constants/theme';

interface PassengerActiveRideProps {
  ride: any; 
  onCancel?: () => void;
}

export default function PassengerActiveRide({ ride, onCancel }: PassengerActiveRideProps) {
  const getStatusText = (status: string) => {
    switch (status) {
      case 'requested': return 'Searching for Driver...';
      case 'accepted': return 'Driver is on the way';
      case 'started': return 'Heading to destination';
      case 'completed': return 'Ride Completed';
      default: return 'Processing...';
    }
  };

  return (
    <View style={styles.container}>
      {/* Top Status Card */}
      <View style={styles.statusCard}>
         <Text style={styles.statusTitle}>{getStatusText(ride.status)}</Text>
         {ride.status !== 'requested' && <Text style={styles.etaText}>ETA: 5 min</Text>}
      </View>

      {/* Driver Info Card (Bottom Sheet style) */}
      <View style={styles.driverCard}>
        {ride.status === 'requested' ? (
            <View style={{ alignItems: 'center', padding: 20 }}>
                <ActivityIndicator size="large" color={COLORS.primary} style={{marginBottom: 20}} />
                <Text style={styles.searchingTitle}>Looking for nearby drivers...</Text>
                <Text style={styles.searchingSubtitle}>Please wait while we connect you.</Text>
                <TouchableOpacity style={styles.cancelButton} onPress={onCancel}>
                    <Text style={styles.cancelText}>Cancel Request</Text>
                </TouchableOpacity>
            </View>
        ) : (
            <>
                <View style={styles.driverHeader}>
                <View style={styles.driverAvatar}>
                    <Text style={styles.avatarText}>{ride.driver?.full_name?.charAt(0) || 'D'}</Text>
                </View>
                <View style={styles.driverInfo}>
                    <Text style={styles.driverName}>{ride.driver?.full_name || 'Driver'}</Text>
                    <Text style={styles.vehicleInfo}>
                        {ride.driver?.vehicle_color} {ride.driver?.vehicle_model} • {ride.driver?.vehicle_plate_number}
                    </Text>
                    <Text style={styles.rating}>4.9 ★</Text>
                </View>
                </View>
                
                <View style={styles.divider} />
                
                <View style={styles.contactRow}>
                <TouchableOpacity style={styles.actionButton}>
                    <Text style={styles.actionText}>📞</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.actionButton}>
                    <Text style={styles.actionText}>💬 Message</Text>
                </TouchableOpacity>
                </View>

                {(ride.status === 'accepted' || ride.status === 'requested') && (
                    <TouchableOpacity style={styles.cancelButton} onPress={onCancel}>
                        <Text style={styles.cancelText}>Cancel Ride</Text>
                    </TouchableOpacity>
                )}
            </>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'space-between',
    padding: 20,
    zIndex: 100,
    pointerEvents: 'box-none', 
  },
  statusCard: {
    backgroundColor: COLORS.card,
    padding: 16,
    borderRadius: 12,
    alignSelf: 'center',
    marginTop: 160, // Clears Role Toggle (at top: 100)
    ...SHADOWS.medium,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  statusTitle: {
    ...TYPOGRAPHY.subheader,
    textAlign: 'center',
  },
  etaText: {
    color: COLORS.primary,
    fontWeight: 'bold',
    textAlign: 'center',
    marginTop: 4,
  },
  driverCard: {
    backgroundColor: COLORS.card,
    borderRadius: 24,
    padding: 24,
    paddingBottom: 40,
    ...SHADOWS.neon,
    borderTopWidth: 2,
    borderTopColor: COLORS.primary,
    marginBottom: 0,
  },
  searchingTitle: {
      ...TYPOGRAPHY.header,
      marginBottom: 8,
      textAlign: 'center',
  },
  searchingSubtitle: {
      ...TYPOGRAPHY.body,
      color: COLORS.textDim,
      textAlign: 'center',
      marginBottom: 20,
  },
  driverHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  driverAvatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  avatarText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  driverInfo: {
    flex: 1,
  },
  driverName: {
    ...TYPOGRAPHY.subheader,
    marginBottom: 4,
  },
  vehicleInfo: {
    ...TYPOGRAPHY.caption,
    marginBottom: 4,
  },
  rating: {
    color: COLORS.accent, 
    fontWeight: 'bold',
  },
  divider: {
    height: 1,
    backgroundColor: COLORS.border,
    marginVertical: 16,
  },
  contactRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
    gap: 12,
  },
  actionButton: {
    padding: 14,
    borderRadius: 12,
    backgroundColor: COLORS.background,
    flex: 1,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  actionText: {
    color: COLORS.text,
    fontWeight: '600',
  },
  cancelButton: {
    marginTop: 10,
    padding: 16,
    alignItems: 'center',
  },
  cancelText: {
    color: COLORS.danger,
    fontWeight: 'bold',
    fontSize: 16,
  },
});
