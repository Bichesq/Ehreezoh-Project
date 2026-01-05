import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { voteService } from '../services/VoteService';
import { useAuth } from '../context/AuthContext';
import { COLORS } from '../constants/colors';

interface IncidentVerificationButtonsProps {
  incidentId: string;
  onVerified?: () => void;
}

export default function IncidentVerificationButtons({ 
  incidentId, 
  onVerified 
}: IncidentVerificationButtonsProps) {
  const { user } = useAuth();
  const [loading, setLoading] = useState<'still_there' | 'all_clear' | null>(null);
  const [verified, setVerified] = useState(false);
  
  const userTrustScore = user?.trust_score ?? 0;
  const canVerify = userTrustScore >= 25;

  const handleVerify = async (type: 'still_there' | 'all_clear') => {
    if (!canVerify) {
      Alert.alert(
        'Trust Score Required',
        'You need a Trust Score of 25+ to verify incidents. Keep reporting to build your trust!',
        [{ text: 'OK' }]
      );
      return;
    }

    setLoading(type);
    try {
      const response = await voteService.verifyIncident(incidentId, type);
      setVerified(true);
      Alert.alert('Thanks!', response.message);
      onVerified?.();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to verify';
      Alert.alert('Error', message);
    } finally {
      setLoading(null);
    }
  };

  if (verified) {
    return (
      <View style={styles.verifiedContainer}>
        <Text style={styles.verifiedText}>✅ Thanks for verifying!</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.promptText}>Is this still happening?</Text>
      
      <View style={styles.buttonRow}>
        <TouchableOpacity
          style={[
            styles.button, 
            styles.stillThereButton,
            !canVerify && styles.disabledButton
          ]}
          onPress={() => handleVerify('still_there')}
          disabled={loading !== null}
        >
          {loading === 'still_there' ? (
            <ActivityIndicator size="small" color="#FFF" />
          ) : (
            <>
              <Text style={styles.buttonIcon}>👍</Text>
              <Text style={styles.buttonText}>Still there</Text>
            </>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.button, 
            styles.allClearButton,
            !canVerify && styles.disabledButton
          ]}
          onPress={() => handleVerify('all_clear')}
          disabled={loading !== null}
        >
          {loading === 'all_clear' ? (
            <ActivityIndicator size="small" color="#FFF" />
          ) : (
            <>
              <Text style={styles.buttonIcon}>✅</Text>
              <Text style={styles.buttonText}>All clear</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {!canVerify && (
        <Text style={styles.trustNote}>
          🔒 Trust Score 25+ required to verify
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    marginTop: 8,
  },
  promptText: {
    fontSize: 12,
    color: COLORS.textDim,
    marginBottom: 8,
    textAlign: 'center',
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 8,
  },
  button: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    gap: 4,
  },
  stillThereButton: {
    backgroundColor: COLORS.primary,
  },
  allClearButton: {
    backgroundColor: '#22c55e',
  },
  disabledButton: {
    opacity: 0.5,
  },
  buttonIcon: {
    fontSize: 14,
  },
  buttonText: {
    color: '#FFF',
    fontWeight: '600',
    fontSize: 13,
  },
  trustNote: {
    fontSize: 11,
    color: COLORS.textDim,
    textAlign: 'center',
    marginTop: 8,
  },
  verifiedContainer: {
    paddingVertical: 12,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    marginTop: 8,
  },
  verifiedText: {
    fontSize: 14,
    color: '#22c55e',
    fontWeight: '600',
  },
});
