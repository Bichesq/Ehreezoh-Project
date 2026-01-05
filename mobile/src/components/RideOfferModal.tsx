import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Dimensions, Animated } from 'react-native';
import { COLORS } from '../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../constants/theme';

interface RideOffer {
    ride_id: string;
    pickup_address: string;
    dropoff_address: string;
    estimated_fare: number;
    distance_km: number;
    pickup_dist_km?: number; // Distance to pickup
}

interface RideOfferModalProps {
    visible: boolean;
    offer: RideOffer | null;
    onAccept: (rideId: string) => void;
    onDecline: () => void;
    timeRemaining?: number; // Optional countdown
}

const { width } = Dimensions.get('window');

export default function RideOfferModal({ visible, offer, onAccept, onDecline, timeRemaining = 30 }: RideOfferModalProps) {
    const slideAnim = useRef(new Animated.Value(Dimensions.get('window').height)).current;
    
    useEffect(() => {
        if (visible) {
            Animated.spring(slideAnim, {
                toValue: 0,
                useNativeDriver: true,
                tension: 50,
                friction: 8
            }).start();
        } else {
            Animated.timing(slideAnim, {
                toValue: Dimensions.get('window').height,
                duration: 300,
                useNativeDriver: true
            }).start();
        }
    }, [visible]);

    if (!offer) return null;

    return (
        <Animated.View style={[styles.container, { transform: [{ translateY: slideAnim }] }]}>
            <View style={styles.content}>
                <View style={styles.header}>
                    <Text style={styles.title}>New Ride Request! 🚕</Text>
                    <Text style={styles.timer}>{timeRemaining}s</Text>
                </View>
                
                <View style={styles.fareContainer}>
                    <Text style={styles.fareLabel}>Estimated Fare</Text>
                    <Text style={styles.fareValue}>{offer.estimated_fare?.toLocaleString()} XAF</Text>
                </View>

                <View style={styles.detailsContainer}>
                    <View style={styles.timelineItem}>
                        <View style={[styles.dot, styles.pickupDot]} />
                        <View style={styles.timelineContent}>
                            <Text style={styles.addressLabel}>PICKUP ({offer.pickup_dist_km?.toFixed(1) || '0.5'} km away)</Text>
                            <Text style={styles.addressText} numberOfLines={2}>{offer.pickup_address}</Text>
                        </View>
                    </View>
                    
                    <View style={styles.line} />
                    
                    <View style={styles.timelineItem}>
                        <View style={[styles.dot, styles.dropoffDot]} />
                        <View style={styles.timelineContent}>
                            <Text style={styles.addressLabel}>DROPOFF ({offer.distance_km?.toFixed(1)} km trip)</Text>
                            <Text style={styles.addressText} numberOfLines={2}>{offer.dropoff_address}</Text>
                        </View>
                    </View>
                </View>

                <View style={styles.actions}>
                    <TouchableOpacity style={styles.declineButton} onPress={onDecline}>
                        <Text style={styles.declineText}>Decline</Text>
                    </TouchableOpacity>
                    
                    <TouchableOpacity style={styles.acceptButton} onPress={() => onAccept(offer.ride_id)}>
                        <Text style={styles.acceptText}>ACCEPT RIDE</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </Animated.View>
    );
}

const styles = StyleSheet.create({
    container: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        justifyContent: 'flex-end',
        backgroundColor: 'rgba(0,0,0,0.5)',
        zIndex: 1000,
    },
    content: {
        backgroundColor: COLORS.card,
        borderTopLeftRadius: 24,
        borderTopRightRadius: 24,
        padding: 24,
        paddingBottom: 40,
        ...SHADOWS.medium,
        borderTopWidth: 2,
        borderColor: COLORS.primary,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 20,
    },
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    timer: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.danger,
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: 8,
        overflow: 'hidden',
    },
    fareContainer: {
        alignItems: 'center',
        marginBottom: 24,
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        padding: 16,
        borderRadius: 16,
        borderWidth: 1,
        borderColor: 'rgba(16, 185, 129, 0.3)',
    },
    fareLabel: {
        fontSize: 14,
        color: COLORS.textDim,
        marginBottom: 4,
        textTransform: 'uppercase',
        letterSpacing: 1,
    },
    fareValue: {
        fontSize: 32,
        fontWeight: '900',
        color: COLORS.primary,
    },
    detailsContainer: {
        marginBottom: 24,
    },
    timelineItem: {
        flexDirection: 'row',
        alignItems: 'flex-start',
    },
    timelineContent: {
        flex: 1,
        marginLeft: 12,
        marginBottom: 4,
    },
    dot: {
        width: 12,
        height: 12,
        borderRadius: 6,
        marginTop: 4,
    },
    pickupDot: {
        backgroundColor: COLORS.primary,
        borderWidth: 2,
        borderColor: COLORS.background,
    },
    dropoffDot: {
        backgroundColor: COLORS.accent,
        borderWidth: 2,
        borderColor: COLORS.background,
    },
    line: {
        width: 2,
        height: 24,
        backgroundColor: COLORS.border,
        marginLeft: 5,
        marginVertical: 4,
    },
    addressLabel: {
        fontSize: 12,
        color: COLORS.textDim,
        fontWeight: '600',
        marginBottom: 2,
    },
    addressText: {
        fontSize: 16,
        color: COLORS.text,
        fontWeight: '500',
    },
    actions: {
        flexDirection: 'row',
        gap: 16,
    },
    declineButton: {
        flex: 1,
        padding: 16,
        backgroundColor: COLORS.background,
        borderRadius: 14,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    declineText: {
        color: COLORS.textDim,
        fontSize: 16,
        fontWeight: '600',
    },
    acceptButton: {
        flex: 2,
        padding: 16,
        backgroundColor: COLORS.primary,
        borderRadius: 14,
        alignItems: 'center',
        ...SHADOWS.neon,
    },
    acceptText: {
        color: COLORS.background,
        fontSize: 18,
        fontWeight: 'bold',
        letterSpacing: 0.5,
    },
});
