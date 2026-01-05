import React, { useState } from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, TextInput, ActivityIndicator, Alert } from 'react-native';
import { incidentService } from '../../services/incident';
import { useAuth } from '../../context/AuthContext';


interface IncidentReportModalProps {
  visible: boolean;
  onClose: () => void;
  location: { latitude: number; longitude: number } | null;
  onReportSuccess: () => void;
}

const INCIDENT_TYPES = [
  { id: 'accident', label: '🚗 Accident', icon: '💥' },
  { id: 'traffic', label: '🚦 Traffic', icon: '🐢' },
  { id: 'police', label: '👮 Police', icon: '👮', minTrust: 50 },
  { id: 'roadblock', label: '🚧 Roadblock', icon: '⛔' },
];

import { COLORS } from '../../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../../constants/theme';

export default function IncidentReportModal({ visible, onClose, location, onReportSuccess }: IncidentReportModalProps) {
  const { user } = useAuth();
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Get user's trust score (defaults to 0 for new users)
  const userTrustScore = user?.trust_score ?? 0;
  
  // Filter out incident types the user doesn't have access to
  const visibleIncidentTypes = INCIDENT_TYPES.filter(type => {
    if (type.minTrust) {
      return userTrustScore >= type.minTrust;
    }
    return true;
  });

  const handleReport = async () => {
    if (!selectedType || !location) return;

    setLoading(true);
    try {
      await incidentService.reportIncident({
        type: selectedType,
        description,
        latitude: location.latitude,
        longitude: location.longitude,
      });
      Alert.alert('Reported', 'Thanks for keeping the community safe!');
      onReportSuccess();
      onClose();
      // Reset
      setSelectedType(null);
      setDescription('');
    } catch (error) {
      console.error('Report error:', error);
      Alert.alert('Error', 'Failed to submit report.');
    } finally {
        setLoading(false);
    }
  };

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.overlay}>
        <View style={styles.container}>
          <Text style={styles.title}>Report Incident</Text>
          <Text style={styles.subtitle}>What's happening nearby?</Text>

          <View style={styles.grid}>
            {visibleIncidentTypes.map((type) => (
              <TouchableOpacity
                key={type.id}
                style={[
                  styles.typeResult,
                  selectedType === type.id && styles.typeSelected,
                ]}
                onPress={() => setSelectedType(type.id)}
              >
                <Text style={styles.typeIcon}>{type.icon}</Text>
                <Text style={[
                    styles.typeLabel,
                    selectedType === type.id && styles.typeLabelSelected,
                ]}>{type.label}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <TextInput
            style={styles.input}
            placeholder="Add a description (optional)..."
            placeholderTextColor={COLORS.textDim}
            value={description}
            onChangeText={setDescription}
            multiline
          />

          <View style={styles.actions}>
            <TouchableOpacity onPress={onClose} style={styles.cancelButton}>
              <Text style={styles.cancelText}>Cancel</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
                onPress={handleReport} 
                style={[styles.submitButton, (!selectedType || loading) && styles.disabled]}
                disabled={!selectedType || loading}
            >
              {loading ? <ActivityIndicator color="#FFF" /> : <Text style={styles.submitText}>Submit Report</Text>}
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  container: {
    backgroundColor: COLORS.card,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    minHeight: 450,
    ...SHADOWS.medium,
    borderTopWidth: 1,
    borderColor: COLORS.border,
  },
  title: {
    ...TYPOGRAPHY.header,
    marginBottom: 8,
  },
  subtitle: {
    ...TYPOGRAPHY.body,
    color: COLORS.textDim,
    marginBottom: 24,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  typeResult: {
    width: '48%',
    backgroundColor: COLORS.background,
    padding: 16,
    borderRadius: 16,
    marginBottom: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  typeSelected: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(2, 221, 237, 0.1)', 
  },
  typeIcon: {
    fontSize: 28,
    marginBottom: 8,
  },
  typeLabel: {
    fontWeight: '600',
    color: COLORS.text,
  },
  typeLabelSelected: {
    color: COLORS.primary,
  },
  input: {
    backgroundColor: COLORS.background,
    borderRadius: 16,
    padding: 16,
    height: 100,
    textAlignVertical: 'top',
    marginBottom: 24,
    color: COLORS.text,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 16,
  },
  cancelButton: {
    padding: 16,
    borderRadius: 16,
    backgroundColor: COLORS.background,
    flex: 1,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  cancelText: {
    fontWeight: 'bold',
    color: COLORS.textDim,
  },
  submitButton: {
      padding: 16,
      borderRadius: 16,
      backgroundColor: COLORS.primary,
      flex: 2,
      alignItems: 'center',
      ...SHADOWS.neon,
  },
  disabled: {
      opacity: 0.5,
      backgroundColor: COLORS.border,
  },
  submitText: {
      color: COLORS.background,
      fontWeight: 'bold',
      fontSize: 16,
  },
});
