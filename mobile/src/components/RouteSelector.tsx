import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { ScoredRoute } from '../services/route';
import { COLORS } from '../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../constants/theme';

interface RouteSelectorProps {
    routes: ScoredRoute[];
    selectedRouteId: string | null;
    onSelect: (route: ScoredRoute) => void;
    onConfirm: () => void;
    onNavigate: () => void;
    onForecast?: () => void;
    onCancel: () => void;
}

export default function RouteSelector({ 
    routes, 
    selectedRouteId, 
    onSelect, 
    onConfirm,
    onNavigate,
    onForecast,
    onCancel 
}: RouteSelectorProps) {

    const selectedRoute = routes.find(r => r.id === selectedRouteId);

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Select Route</Text>
            
            <ScrollView 
                horizontal 
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.scrollContainer}
            >
                {routes.map(route => {
                    const isSelected = route.id === selectedRouteId;
                    return (
                        <TouchableOpacity 
                            key={route.id}
                            style={[
                                styles.card, 
                                isSelected && styles.selectedCard
                            ]}
                            onPress={() => onSelect(route)}
                        >
                            {/* Header Label */}
                            <View style={[
                                styles.labelBadge, 
                                { backgroundColor: getScoreColor(route.score) }
                            ]}>
                                <Text style={styles.labelText}>{route.label}</Text>
                            </View>

                            {/* Stats */}
                            <View style={styles.statsContainer}>
                                <Text style={styles.durationText}>{route.duration_minutes} min</Text>
                                <Text style={styles.distanceText}>{route.distance_km} km</Text>
                            </View>

                            {/* Warnings / Incidents */}
                            {route.incidents.length > 0 ? (
                                <View style={styles.incidentsContainer}>
                                    <Text style={styles.warningText}>
                                        ⚠️ {route.incidents.length} incidents reported
                                    </Text>
                                </View>
                            ) : (
                                <View style={styles.incidentsContainer}>
                                    <Text style={styles.safeText}>✅ Clear Route</Text>
                                </View>
                            )}
                        </TouchableOpacity>
                    );
                })}
            </ScrollView>

            <View style={styles.actionRow}>
                <TouchableOpacity style={styles.cancelButton} onPress={onCancel}>
                    <Text style={styles.cancelText}>Cancel</Text>
                </TouchableOpacity>

                {/* Forecast Button */}
                {onForecast && (
                    <TouchableOpacity 
                        style={[styles.forecastButton, !selectedRoute && styles.disabledButton]}
                        onPress={onForecast}
                        disabled={!selectedRoute}
                    >
                        <Text style={styles.forecastText}>📅</Text>
                    </TouchableOpacity>
                )}

                <TouchableOpacity 
                    style={[styles.navButton, !selectedRoute && styles.disabledButton]} 
                    onPress={onNavigate}
                    disabled={!selectedRoute}
                >
                    <Text style={styles.navText}>Start Nav 🧭</Text>
                </TouchableOpacity>

                <TouchableOpacity 
                    style={[styles.confirmButton, !selectedRoute && styles.disabledButton]} 
                    onPress={onConfirm}
                    disabled={!selectedRoute}
                >
                    <Text style={styles.confirmText}>Book Ride</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}

function getScoreColor(score: number): string {
    if (score >= 80) return COLORS.success; // Green
    if (score >= 60) return COLORS.secondary; // Orange/Yellow
    return COLORS.danger; // Red
}

const styles = StyleSheet.create({
    container: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: COLORS.card,
        borderTopLeftRadius: 24,
        borderTopRightRadius: 24,
        padding: 20,
        paddingBottom: 40,
        ...SHADOWS.medium,
        borderTopWidth: 1,
        borderTopColor: COLORS.border,
    },
    title: {
        ...TYPOGRAPHY.header,
        marginBottom: 15,
        color: COLORS.text,
    },
    scrollContainer: {
        paddingRight: 20,
        gap: 15,
        marginBottom: 20,
    },
    card: {
        width: 160,
        backgroundColor: COLORS.background,
        borderRadius: 16,
        padding: 12,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    selectedCard: {
        borderColor: COLORS.primary,
        backgroundColor: 'rgba(56, 189, 248, 0.1)', // Primary transparent
        ...SHADOWS.neon,
    },
    labelBadge: {
        alignSelf: 'flex-start',
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 8,
        marginBottom: 8,
    },
    labelText: {
        color: '#fff',
        fontWeight: 'bold',
        fontSize: 12,
    },
    statsContainer: {
        marginBottom: 8,
    },
    durationText: {
        color: COLORS.text,
        fontSize: 18,
        fontWeight: 'bold',
    },
    distanceText: {
        color: COLORS.textDim,
        fontSize: 14,
    },
    incidentsContainer: {
        marginTop: 4,
    },
    warningText: {
        color: COLORS.danger,
        fontSize: 12,
        fontWeight: '600',
    },
    safeText: {
        color: COLORS.success,
        fontSize: 12,
        fontWeight: '600',
    },
    actionRow: {
        flexDirection: 'row',
        gap: 15,
    },
    cancelButton: {
        padding: 16,
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
    },
    cancelText: {
        color: COLORS.textDim,
        fontWeight: 'bold',
    },
    confirmButton: {
        backgroundColor: COLORS.primary,
        padding: 16,
        borderRadius: 16,
        flex: 2,
        alignItems: 'center',
        justifyContent: 'center',
        ...SHADOWS.neon,
    },
    disabledButton: {
        opacity: 0.5,
        shadowOpacity: 0,
    },
    confirmText: {
        color: COLORS.background,
        fontWeight: 'bold',
        fontSize: 14,
    },
    navButton: {
        backgroundColor: COLORS.secondary,
        padding: 16,
        borderRadius: 16,
        flex: 1.5,
        alignItems: 'center',
        justifyContent: 'center',
        ...SHADOWS.medium,
    },
    navText: {
        color: COLORS.background,
        fontWeight: 'bold',
        fontSize: 14,
    },
    forecastButton: {
        backgroundColor: COLORS.card,
        padding: 16,
        borderRadius: 16,
        borderWidth: 1,
        borderColor: COLORS.border,
        alignItems: 'center',
        justifyContent: 'center',
        ...SHADOWS.medium,
    },
    forecastText: {
        fontSize: 20
    }
});
