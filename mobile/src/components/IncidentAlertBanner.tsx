import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import { COLORS } from '../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../constants/theme';

interface IncidentAlert {
    id: string;
    type: string;
    description: string;
    latitude: number;
    longitude: number;
}

interface IncidentAlertBannerProps {
    alert: IncidentAlert | null;
    onDismiss: () => void;
    onView?: (alert: any) => void;
    onReroute?: () => void;
}

export default function IncidentAlertBanner({ alert, onDismiss, onView, onReroute }: IncidentAlertBannerProps) {
    const slideAnim = useRef(new Animated.Value(-100)).current;

    useEffect(() => {
        if (alert) {
            Animated.spring(slideAnim, {
                toValue: 0,
                useNativeDriver: true,
            }).start();
        } else {
            Animated.timing(slideAnim, {
                toValue: -100,
                duration: 300,
                useNativeDriver: true,
            }).start();
        }
    }, [alert]);

    if (!alert) return null;

    return (
        <Animated.View style={[styles.container, { transform: [{ translateY: slideAnim }] }]}>
            <View style={styles.iconContainer}>
                <Text style={styles.iconText}>⚠️</Text>
            </View>
            
            <View style={styles.contentContainer}>
                <Text style={styles.title}>New Incident Reported</Text>
                <Text style={styles.message}>
                    {alert.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} ahead.
                    {alert.description ? ` "${alert.description}"` : ''}
                </Text>
            </View>

                <View style={styles.actions}>
                    {onReroute && (
                        <TouchableOpacity style={[styles.button, styles.rerouteButton]} onPress={onReroute}>
                            <Text style={styles.rerouteText}>REROUTE</Text>
                        </TouchableOpacity>
                    )}
                    {onView && (
                        <TouchableOpacity style={styles.button} onPress={() => onView(alert)}>
                            <Text style={styles.buttonText}>VIEW</Text>
                        </TouchableOpacity>
                    )}
                    <TouchableOpacity style={styles.iconButton} onPress={onDismiss}>
                        <Text style={styles.dismissText}>✕</Text>
                    </TouchableOpacity>
                </View>
        </Animated.View>
    );
}

const styles = StyleSheet.create({
    container: {
        position: 'absolute',
        top: 60, // Clear status bar
        left: 20,
        right: 20,
        backgroundColor: '#000000', // Pitch black for neon contrast
        borderRadius: 16,
        flexDirection: 'row',
        padding: 16,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: COLORS.danger,
        shadowColor: COLORS.danger,
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.8,
        shadowRadius: 10,
        elevation: 10,
        zIndex: 999,
        // No left border, full neon glow
    },
    iconContainer: {
        marginRight: 12,
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        padding: 8,
        borderRadius: 20,
    },
    iconText: {
        fontSize: 20,
    },
    contentContainer: {
        flex: 1,
    },
    title: {
        color: COLORS.danger,
        fontWeight: 'bold',
        fontSize: 14,
        marginBottom: 2,
    },
    message: {
        color: COLORS.text,
        fontSize: 12,
    },
    actions: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingLeft: 10,
    },
    button: {
        paddingVertical: 8,
        paddingHorizontal: 12,
        borderRadius: 8,
        backgroundColor: COLORS.primaryLight,
        marginLeft: 8,
    },
    iconButton: {
        padding: 8,
        marginLeft: 8,
    },
    rerouteButton: {
        backgroundColor: COLORS.warning,
        marginRight: 8,
    },
    rerouteText: {
        color: '#000',
        fontWeight: 'bold',
        fontSize: 12,
    },
    buttonText: {
        color: COLORS.primary,
        fontWeight: 'bold',
        fontSize: 12,
    },
    dismissText: {
        color: COLORS.textDim,
        fontSize: 16,
        fontWeight: 'bold',
    }
});
