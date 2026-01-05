import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, Image, ScrollView, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';

import { incidentService } from '../../src/services/incident';
import { COLORS } from '../../src/constants/colors'; // Assuming this exists, based on other files usually having constants

// Fallback colors if constant file not found/checked
const THEME = {
  primary: '#FF3B30', // Red for emergency/danger
  background: '#121212',
  card: '#1E1E1E',
  text: '#FFFFFF',
  textSecondary: '#AAAAAA',
  border: '#333333',
};

const INCIDENT_TYPES = [
  { id: 'traffic', label: 'Heavy Traffic', icon: 'car' },
  { id: 'accident', label: 'Accident', icon: 'alert-circle' },
  { id: 'hazard', label: 'Road Hazard', icon: 'warning' },
  { id: 'police', label: 'Police/Check', icon: 'shield' },
];

export default function ReportScreen() {
  const router = useRouter();
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [address, setAddress] = useState<string>('Fetching location...');
  const [photo, setPhoto] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission to access location was denied');
        setAddress('Location permission denied');
        setLoading(false);
        return;
      }

      try {
        let location = await Location.getCurrentPositionAsync({});
        setLocation(location);
        
        // Reverse geocode for better UX
        let reverseGeocode = await Location.reverseGeocodeAsync({
          latitude: location.coords.latitude,
          longitude: location.coords.longitude
        });

        if (reverseGeocode.length > 0) {
          const addr = reverseGeocode[0];
          setAddress(`${addr.street || ''} ${addr.city || ''}`.trim() || 'Unknown location');
        } else {
            setAddress(`${location.coords.latitude.toFixed(4)}, ${location.coords.longitude.toFixed(4)}`);
        }
      } catch (error) {
        setAddress('Could not fetch location');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.5,
    });

    if (!result.canceled) {
      setPhoto(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (permission.status !== 'granted') {
        Alert.alert("Camera permission denied");
        return;
    }

    const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.5,
    });

    if (!result.canceled) {
        setPhoto(result.assets[0].uri);
    }
  };

  const handleSubmit = async () => {
    if (!selectedType) {
      Alert.alert('Please select an incident type');
      return;
    }
    if (!location) {
      Alert.alert('Location not verified yet');
      return;
    }

    setSubmitting(true);
    try {
      const result = await incidentService.reportIncident({
        type: selectedType,
        description: description,
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        media_url: photo || undefined, // Passing URI as media_url for now (will be handled by sync/backend later)
      });
      
      Alert.alert(
        'Report Submitted', 
        result.status === 'queued' ? 'You are offline. Report queued.' : 'Thanks for keeping the community safe!',
        [{ text: 'OK', onPress: () => router.back() }]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to submit report. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#FFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Report Incident</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.content}>
        
        {/* Location Section */}
        <View style={styles.section}>
          <Text style={styles.label}>Location</Text>
          <View style={styles.locationCard}>
             <Ionicons name="location" size={20} color={THEME.primary} />
             <Text style={styles.locationText}>{address}</Text>
             {loading && <ActivityIndicator size="small" color={THEME.primary} style={{marginLeft: 10}}/>}
          </View>
        </View>

        {/* Incident Type Section */}
        <View style={styles.section}>
          <Text style={styles.label}>Incident Type</Text>
          <View style={styles.grid}>
            {INCIDENT_TYPES.map((type) => (
              <TouchableOpacity
                key={type.id}
                style={[
                  styles.typeButton,
                  selectedType === type.id && styles.typeButtonSelected
                ]}
                onPress={() => setSelectedType(type.id)}
              >
                <Ionicons 
                    name={type.icon as any} 
                    size={28} 
                    color={selectedType === type.id ? '#FFF' : THEME.textSecondary} 
                />
                <Text style={[
                  styles.typeLabel,
                  selectedType === type.id && styles.typeLabelSelected
                ]}>
                  {type.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Description Section */}
        <View style={styles.section}>
          <Text style={styles.label}>Description (Optional)</Text>
          <TextInput
            style={styles.input}
            placeholder="Add more details..."
            placeholderTextColor="#666"
            multiline
            numberOfLines={3}
            value={description}
            onChangeText={setDescription}
          />
        </View>

        {/* Photo Section */}
        <View style={styles.section}>
          <Text style={styles.label}>Photo (Optional)</Text>
          <View style={styles.photoRow}>
             <TouchableOpacity style={styles.photoButton} onPress={takePhoto}>
                <Ionicons name="camera" size={24} color={THEME.primary} />
                <Text style={styles.photoButtonText}>Camera</Text>
             </TouchableOpacity>
             <TouchableOpacity style={styles.photoButton} onPress={pickImage}>
                <Ionicons name="images" size={24} color={THEME.primary} />
                <Text style={styles.photoButtonText}>Gallery</Text>
             </TouchableOpacity>
          </View>
          
          {photo && (
            <View style={styles.previewContainer}>
                <Image source={{ uri: photo }} style={styles.photoPreview} />
                <TouchableOpacity 
                    style={styles.removePhoto}
                    onPress={() => setPhoto(null)}
                >
                    <Ionicons name="close-circle" size={24} color="#FFF" />
                </TouchableOpacity>
            </View>
          )}
        </View>

      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity 
            style={[styles.submitButton, (submitting || loading) && styles.disabledButton]}
            onPress={handleSubmit}
            disabled={submitting || loading}
        >
            {submitting ? (
                <ActivityIndicator color="#FFF" />
            ) : (
                <Text style={styles.submitText}>Submit Report</Text>
            )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: THEME.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 20,
    backgroundColor: THEME.card,
  },
  headerTitle: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  backButton: {
    padding: 4,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  section: {
    marginBottom: 24,
  },
  label: {
    color: THEME.textSecondary,
    marginBottom: 10,
    fontSize: 14,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  locationCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: THEME.card,
    padding: 16,
    borderRadius: 12,
  },
  locationText: {
    color: '#FFF',
    marginLeft: 10,
    fontSize: 16,
    flex: 1,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 10,
  },
  typeButton: {
    width: '48%',
    backgroundColor: THEME.card,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'transparent',
  },
  typeButtonSelected: {
    backgroundColor: '#331111',
    borderColor: THEME.primary,
  },
  typeLabel: {
    color: THEME.textSecondary,
    marginTop: 8,
    fontWeight: '500',
  },
  typeLabelSelected: {
    color: '#FFF',
  },
  input: {
    backgroundColor: THEME.card,
    borderRadius: 12,
    padding: 16,
    color: '#FFF',
    fontSize: 16,
    textAlignVertical: 'top',
    minHeight: 100,
  },
  photoRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  photoButton: {
    flex: 1,
    backgroundColor: THEME.card,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 12,
    gap: 8,
  },
  photoButtonText: {
    color: '#FFF',
    fontWeight: '500',
  },
  previewContainer: {
    marginTop: 10,
    position: 'relative',
    alignSelf: 'flex-start',
  },
  photoPreview: {
    width: 100,
    height: 100,
    borderRadius: 12,
  },
  removePhoto: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 12,
  },
  footer: {
    padding: 20,
    backgroundColor: THEME.card,
    paddingBottom: Platform.OS === 'ios' ? 40 : 20, // Safe area
  },
  submitButton: {
    backgroundColor: THEME.primary,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  disabledButton: {
    opacity: 0.7,
  },
  submitText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
