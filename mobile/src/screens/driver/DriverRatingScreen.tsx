import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, Alert, ActivityIndicator } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { driverService } from '../../services/driver';

interface DriverRatingScreenProps {
  ride: any;
  onComplete: () => void;
}

import { COLORS } from '../../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../../constants/theme';

export default function DriverRatingScreen({ ride, onComplete }: DriverRatingScreenProps) {
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (rating === 0) {
      Alert.alert('Rating Required', 'Please rate the passenger.');
      return;
    }

    setSubmitting(true);
    try {
      await driverService.ratePassenger(ride.id, rating, review);
      Alert.alert('Success', 'Rating submitted.');
      onComplete();
    } catch (error) {
      console.error('Rating error:', error);
      Alert.alert('Error', 'Failed to submit rating.');
    } finally {
      setSubmitting(false);
    }
  };

  const renderStars = () => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <TouchableOpacity key={i} onPress={() => setRating(i)}>
          <Text style={[styles.star, i <= rating && styles.selectedStar]}>★</Text>
        </TouchableOpacity>
      );
    }
    return <View style={styles.starsContainer}>{stars}</View>;
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <View style={styles.card}>
        <Text style={styles.title}>Ride Completed</Text>
        
        <View style={styles.infoContainer}>
            <Text style={styles.label}>Passenger</Text>
            <Text style={styles.value}>{ride.passenger?.full_name || 'Passenger'}</Text>
        </View>

        <View style={styles.fareContainer}>
            <Text style={styles.label}>Collect Cash</Text>
            <Text style={styles.fareAmount}>{ride.final_fare || ride.estimated_fare} XAF</Text>
        </View>

        <Text style={styles.subtitle}>Rate Passenger</Text>
        {renderStars()}

        <TextInput
          style={styles.input}
          placeholder="Comments (optional)..."
          placeholderTextColor={COLORS.textDim}
          multiline
          value={review}
          onChangeText={setReview}
        />

        <TouchableOpacity 
            style={[styles.submitButton, submitting && styles.disabledButton]} 
            onPress={handleSubmit}
            disabled={submitting}
        >
          {submitting ? (
             <ActivityIndicator color={COLORS.background} />
          ) : (
             <Text style={styles.buttonText}>Submit & Go Online</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: COLORS.background, 
    padding: 20,
    justifyContent: 'center',
  },
  card: {
    alignItems: 'center',
    backgroundColor: COLORS.card,
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: COLORS.primary,
    ...SHADOWS.neon,
  },
  title: {
    ...TYPOGRAPHY.header,
    marginBottom: 30,
    color: COLORS.primary,
  },
  infoContainer: {
    marginBottom: 20,
    alignItems: 'center',
  },
  fareContainer: {
    marginBottom: 40,
    alignItems: 'center',
    backgroundColor: COLORS.background,
    padding: 20,
    borderRadius: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  label: {
    color: COLORS.textDim,
    fontSize: 16,
    marginBottom: 5,
  },
  value: {
    ...TYPOGRAPHY.subheader,
    fontSize: 20,
  },
  fareAmount: {
    fontSize: 32,
    fontWeight: 'bold',
    color: COLORS.accent,
    textShadowColor: COLORS.accent,
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  subtitle: {
    ...TYPOGRAPHY.subheader,
    marginBottom: 10,
    fontWeight: '600',
  },
  starsContainer: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  star: {
    fontSize: 44,
    color: COLORS.textDim,
    marginHorizontal: 8,
  },
  selectedStar: {
    color: COLORS.accent,
  },
  input: {
    width: '100%',
    height: 100,
    borderColor: COLORS.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 15,
    marginBottom: 20,
    textAlignVertical: 'top',
    backgroundColor: COLORS.background,
    color: COLORS.text,
  },
  submitButton: {
    backgroundColor: COLORS.primary,
    paddingVertical: 18,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
    ...SHADOWS.neon,
  },
  disabledButton: {
    backgroundColor: COLORS.border,
    opacity: 0.5,
  },
  buttonText: {
    color: COLORS.background,
    fontWeight: 'bold',
    fontSize: 18,
  },
});
