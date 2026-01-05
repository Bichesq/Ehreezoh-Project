import React, { useState, useEffect } from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { socialService, ThanksInfo } from '../services/social';
import { COLORS } from '../constants/colors';

interface ThanksButtonProps {
  incidentId: string;
  reporterId?: string;
  currentUserId?: string;
  initialThanks?: number;
}

export default function ThanksButton({ 
  incidentId, 
  reporterId, 
  currentUserId,
  initialThanks = 0 
}: ThanksButtonProps) {
  const [loading, setLoading] = useState(false);
  const [hasThanked, setHasThanked] = useState(false);
  const [totalThanks, setTotalThanks] = useState(initialThanks);
  const [checked, setChecked] = useState(false);

  // Don't show for own reports
  if (reporterId && currentUserId && reporterId === currentUserId) {
    return null;
  }

  useEffect(() => {
    checkThanksStatus();
  }, [incidentId]);

  const checkThanksStatus = async () => {
    try {
      const info = await socialService.getThanksInfo(incidentId);
      setHasThanked(info.has_thanked);
      setTotalThanks(info.total_thanks);
    } catch (error) {
      // Silent fail
    } finally {
      setChecked(true);
    }
  };

  const handleThanks = async () => {
    if (hasThanked || loading) return;

    setLoading(true);
    try {
      const result = await socialService.sayThanks(incidentId);
      setHasThanked(true);
      setTotalThanks(result.total_thanks);
      Alert.alert('💙 Thanks Sent!', 'The reporter has been notified.');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Could not send thanks';
      if (!message.includes('already thanked')) {
        Alert.alert('Oops', message);
      } else {
        setHasThanked(true);
      }
    } finally {
      setLoading(false);
    }
  };

  if (!checked) return null;

  return (
    <TouchableOpacity 
      style={[styles.button, hasThanked && styles.thankedButton]}
      onPress={handleThanks}
      disabled={hasThanked || loading}
    >
      {loading ? (
        <ActivityIndicator size="small" color={COLORS.primary} />
      ) : (
        <Text style={[styles.text, hasThanked && styles.thankedText]}>
          {hasThanked ? '💙 Thanked' : '💙 Say Thanks'} 
          {totalThanks > 0 && ` (${totalThanks})`}
        </Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.primary,
    alignItems: 'center',
    marginTop: 12,
  },
  thankedButton: {
    backgroundColor: 'rgba(2, 221, 237, 0.15)',
    borderColor: 'rgba(2, 221, 237, 0.5)',
  },
  text: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.primary,
  },
  thankedText: {
    color: COLORS.textDim,
  },
});
