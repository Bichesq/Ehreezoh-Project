import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { COLORS } from '../constants/colors';
import { LAYOUT, SHADOWS, TYPOGRAPHY } from '../constants/theme';

interface RideRequestSheetProps {
    distanceKm: number;
    onRequest: (rideType: 'moto' | 'car') => void;
    isLoading: boolean;
    onClose: () => void;
}

export default function RideRequestSheet({ distanceKm, onRequest, isLoading, onClose }: RideRequestSheetProps) {
    const [selectedType, setSelectedType] = useState<'moto' | 'car'>('moto');

    // Simple mock pricing logic
    const motoPrice = Math.max(50, Math.round(distanceKm * 15 + 20)); // Base 20 + 15/km
    const carPrice = Math.max(100, Math.round(distanceKm * 30 + 50));  // Base 50 + 30/km

    return (
        <View style={styles.container}>
            <View style={styles.handle} />
            <Text style={styles.title}>Confirm Ride</Text>

            <View style={styles.infoRow}>
                <Text style={styles.distanceText}>Trip Distance: <Text style={{color: COLORS.primary}}>{distanceKm.toFixed(1)} km</Text></Text>
            </View>

            {/* Vehicle Selection */}
            <View style={styles.optionsContainer}>
                <TouchableOpacity 
                    style={[
                        styles.optionCard, 
                        selectedType === 'moto' && styles.selectedCardMoto
                    ]}
                    onPress={() => setSelectedType('moto')}
                >
                    <Text style={styles.icon}>🏍️</Text>
                    <View style={styles.optionDetails}>
                        <Text style={styles.optionTitle}>Moto</Text>
                        <Text style={styles.optionSubtitle}>Faster • 1 min away</Text>
                    </View>
                    <Text style={styles.priceText}>₹{motoPrice}</Text>
                </TouchableOpacity>

                <TouchableOpacity 
                    style={[
                        styles.optionCard, 
                        selectedType === 'car' && styles.selectedCardCar
                    ]}
                    onPress={() => setSelectedType('car')}
                >
                    <Text style={styles.icon}>🚗</Text>
                    <View style={styles.optionDetails}>
                        <Text style={styles.optionTitle}>Car</Text>
                        <Text style={styles.optionSubtitle}>Comfort • 4 min away</Text>
                    </View>
                    <Text style={styles.priceText}>₹{carPrice}</Text>
                </TouchableOpacity>
            </View>

            {/* Action Buttons */}
            <TouchableOpacity 
                style={[
                    styles.requestButton, 
                    { backgroundColor: selectedType === 'moto' ? COLORS.primary : COLORS.secondary },
                    isLoading && styles.disabledButton
                ]} 
                onPress={() => onRequest(selectedType)}
                disabled={isLoading}
            >
                {isLoading ? (
                    <ActivityIndicator color={COLORS.background} />
                ) : (
                    <Text style={styles.buttonText}>Request {selectedType === 'moto' ? 'Moto' : 'Car'}</Text>
                )}
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.cancelButton} onPress={onClose} disabled={isLoading}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: COLORS.background, // Dark background
        borderTopLeftRadius: 24,
        borderTopRightRadius: 24,
        padding: 24,
        paddingBottom: 40,
        ...SHADOWS.medium,
        borderTopWidth: 1,
        borderTopColor: COLORS.border,
    },
    handle: {
        width: 40,
        height: 4,
        backgroundColor: COLORS.border,
        borderRadius: 2,
        alignSelf: 'center',
        marginBottom: 20,
    },
    title: {
        ...TYPOGRAPHY.header,
        marginBottom: 8,
    },
    infoRow: {
        marginBottom: 24,
    },
    distanceText: {
        ...TYPOGRAPHY.body,
    },
    optionsContainer: {
        gap: 16,
        marginBottom: 32,
    },
    optionCard: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 16,
        backgroundColor: COLORS.card,
        borderRadius: 16,
        borderWidth: 2,
        borderColor: 'transparent',
    },
    selectedCardMoto: {
        borderColor: COLORS.primary,
        backgroundColor: 'rgba(16, 185, 129, 0.1)', // Tinted primary
    },
    selectedCardCar: {
        borderColor: COLORS.secondary,
        backgroundColor: 'rgba(59, 130, 246, 0.1)', // Tinted secondary
    },
    icon: {
        fontSize: 32,
        marginRight: 16,
    },
    optionDetails: {
        flex: 1,
    },
    optionTitle: {
        ...TYPOGRAPHY.subheader,
    },
    optionSubtitle: {
        ...TYPOGRAPHY.caption,
        marginTop: 4,
    },
    priceText: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    requestButton: {
        padding: 20,
        borderRadius: 16,
        alignItems: 'center',
        marginBottom: 12,
        ...SHADOWS.neon, // Glow effect
    },
    disabledButton: {
        backgroundColor: COLORS.card,
        opacity: 0.7,
        shadowOpacity: 0,
    },
    buttonText: {
        color: COLORS.background,
        fontSize: 18,
        fontWeight: 'bold',
    },
    cancelButton: {
        padding: 12,
        alignItems: 'center',
    },
    cancelButtonText: {
        color: COLORS.textDim,
        fontWeight: '600',
    },
});
