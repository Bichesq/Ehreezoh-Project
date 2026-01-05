import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, Alert, ActivityIndicator } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { rideService } from '../../services/ride';

interface RideRatingScreenProps {
  ride: any;
  onComplete: () => void;
}

import { COLORS } from '../../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../../constants/theme';

export default function RideRatingScreen({ ride, onComplete }: RideRatingScreenProps) {
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (rating === 0) {
      Alert.alert('Rating Required', 'Please select a star rating.');
      return;
    }

    setSubmitting(true);
    try {
      await rideService.rateRide(ride.id, rating, review);
      Alert.alert('Thank You!', 'Your rating has been submitted.');
      onComplete();
    } catch (error) {
      console.error('Rating error:', error);
      Alert.alert('Error', 'Failed to submit rating. Please try again.');
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
        <Text style={styles.title}>Ride Completed! 🎉</Text>
        
        <View style={styles.fareContainer}>
            <Text style={styles.fareLabel}>Total Fare</Text>
            <Text style={styles.fareAmount}>{ride.final_fare || ride.estimated_fare} XAF</Text>
        </View>

        <Text style={styles.subtitle}>How was your ride?</Text>
        {renderStars()}

        <TextInput
          style={styles.input}
          placeholder="Leave a comment (optional)..."
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
             <Text style={styles.buttonText}>Submit Rating</Text>
          )}
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.skipButton} onPress={onComplete}>
           <Text style={styles.skipText}>Skip Rating</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.85)', 
    justifyContent: 'center',
    padding: 20,
    zIndex: 200,
  },
  card: {
    backgroundColor: COLORS.card,
    borderRadius: 24,
    padding: 24,
    alignItems: 'center',
    ...SHADOWS.neon,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  title: {
    ...TYPOGRAPHY.header,
    marginBottom: 20,
    color: COLORS.primary,
  },
  fareContainer: {
    alignItems: 'center',
    marginBottom: 24,
    padding: 16,
    backgroundColor: COLORS.background,
    borderRadius: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  fareLabel: {
    ...TYPOGRAPHY.caption,
    fontSize: 14,
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
    marginBottom: 12,
  },
  starsContainer: {
    flexDirection: 'row',
    marginBottom: 24,
  },
  star: {
    fontSize: 40,
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
    borderRadius: 16,
    padding: 16,
    marginBottom: 24,
    textAlignVertical: 'top',
    backgroundColor: COLORS.background,
    color: COLORS.text,
  },
  submitButton: {
    backgroundColor: COLORS.primary,
    paddingVertical: 16,
    paddingHorizontal: 40,
    borderRadius: 16,
    width: '100%',
    alignItems: 'center',
    marginBottom: 16,
    ...SHADOWS.neon,
  },
  disabledButton: {
    backgroundColor: COLORS.border,
    opacity: 0.5,
  },
  buttonText: {
    color: COLORS.background,
    fontWeight: 'bold',
    fontSize: 16,
  },
  skipButton: {
    padding: 10,
  },
  skipText: {
    color: COLORS.textDim,
    textDecorationLine: 'underline',
  },
});
