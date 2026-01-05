import React from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, ScrollView } from 'react-native';
import { COLORS } from '../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../constants/theme';
import { SafetyPrediction } from '../services/analytics';

interface SafetyForecastModalProps {
    visible: boolean;
    onClose: () => void;
    predictions: SafetyPrediction[];
    loading: boolean;
}

export default function SafetyForecastModal({ visible, onClose, predictions, loading }: SafetyForecastModalProps) {
    if (!visible) return null;

    const getBarColor = (score: number) => {
        if (score >= 80) return COLORS.success;
        if (score >= 60) return COLORS.warning;
        return COLORS.danger;
    };

    return (
        <Modal transparent animationType="slide" visible={visible} onRequestClose={onClose}>
            <View style={styles.overlay}>
                <View style={styles.modalContainer}>
                    <Text style={styles.title}>📅 Best Time to Leave</Text>
                    <Text style={styles.subtitle}>Forecast based on historical incident data</Text>
                    
                    {loading ? (
                         <Text style={{color: COLORS.text, marginVertical: 20}}>Analyzing history...</Text>
                    ) : (
                        <View style={styles.chartContainer}>
                            {predictions.map((pred, index) => {
                                const height = Math.max(20, pred.safety_score); // Min height 20
                                const isSafest = index === 0 || predictions.every(p => p.safety_score <= pred.safety_score); // Simple best logic check
                                
                                return (
                                    <View key={index} style={styles.barItem}>
                                        <Text style={styles.barScore}>{pred.safety_score}%</Text>
                                        <View style={[
                                            styles.bar, 
                                            { height: height, backgroundColor: getBarColor(pred.safety_score) },
                                            isSafest && { borderColor: '#fff', borderWidth: 2 }
                                        ]} />
                                        <Text style={styles.barLabel}>{pred.time_label}</Text>
                                        {isSafest && <Text style={styles.safestBadge}>Best</Text>}
                                    </View>
                                );
                            })}
                        </View>
                    )}

                    <TouchableOpacity style={styles.closeButton} onPress={onClose}>
                        <Text style={styles.closeText}>Close</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </Modal>
    );
}

const styles = StyleSheet.create({
    overlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'center',
        padding: 20,
    },
    modalContainer: {
        backgroundColor: COLORS.card,
        borderRadius: 20,
        padding: 20,
        alignItems: 'center',
        ...SHADOWS.medium,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    title: {
        ...TYPOGRAPHY.header,
        marginBottom: 5,
        color: COLORS.text,
    },
    subtitle: {
        color: COLORS.textDim,
        marginBottom: 20,
        fontSize: 14,
    },
    chartContainer: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        alignItems: 'flex-end',
        height: 180,
        width: '100%',
        marginBottom: 20,
        paddingBottom: 10,
        borderBottomWidth: 1,
        borderColor: COLORS.border,
    },
    barItem: {
        alignItems: 'center',
        justifyContent: 'flex-end',
        width: 60,
    },
    bar: {
        width: 30,
        borderRadius: 5,
        marginVertical: 5,
    },
    barLabel: {
        color: COLORS.textDim,
        fontSize: 12,
        fontWeight: 'bold',
    },
    barScore: {
        color: COLORS.text,
        fontSize: 12,
        fontWeight: 'bold',
    },
    safestBadge: {
        color: COLORS.primary,
        fontSize: 10,
        fontWeight: 'bold',
        marginTop: 2,
    },
    closeButton: {
        backgroundColor: COLORS.border,
        paddingVertical: 12,
        paddingHorizontal: 30,
        borderRadius: 20,
    },
    closeText: {
        color: COLORS.text,
        fontWeight: 'bold',
    }
});
