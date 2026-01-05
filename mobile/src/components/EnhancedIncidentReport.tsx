import React, { useState, useEffect } from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Image,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { incidentService } from '../services/incident';
import { useAuth } from '../context/AuthContext';
import { COLORS } from '../constants/colors';

interface EnhancedIncidentReportProps {
  visible: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const INCIDENT_TYPES = [
  { id: 'accident', icon: '💥', label: 'Accident' },
  { id: 'police', icon: '👮', label: 'Police', requiresTrust: 50 },
  { id: 'checkpoint', icon: '🛑', label: 'Checkpoint', requiresTrust: 50 },
  { id: 'traffic', icon: '🐢', label: 'Traffic Jam' },
  { id: 'roadblock', icon: '⛔', label: 'Roadblock' },
  { id: 'hazard', icon: '⚠️', label: 'Hazard' },
  { id: 'flood', icon: '🌊', label: 'Flooding' },
  { id: 'construction', icon: '🚧', label: 'Construction' },
];

export default function EnhancedIncidentReport({ 
  visible, 
  onClose, 
  onSuccess 
}: EnhancedIncidentReportProps) {
  const { user } = useAuth();
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [description, setDescription] = useState('');
  const [photo, setPhoto] = useState<string | null>(null);
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [locationName, setLocationName] = useState('Getting location...');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (visible) {
      getLocation();
    }
  }, [visible]);

  const getLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setLocationName('Location permission denied');
        return;
      }

      const loc = await Location.getCurrentPositionAsync({});
      setLocation({
        latitude: loc.coords.latitude,
        longitude: loc.coords.longitude,
      });

      // Get address
      const addresses = await Location.reverseGeocodeAsync({
        latitude: loc.coords.latitude,
        longitude: loc.coords.longitude,
      });
      
      if (addresses[0]) {
        const addr = addresses[0];
        setLocationName(
          [addr.street, addr.district, addr.city].filter(Boolean).join(', ') || 'Current Location'
        );
      } else {
        setLocationName('Current Location');
      }
    } catch (error) {
      setLocationName('Could not get location');
    }
  };

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please allow access to photos');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [16, 9],
      quality: 0.7,
    });

    if (!result.canceled && result.assets[0]) {
      setPhoto(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please allow camera access');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [16, 9],
      quality: 0.7,
    });

    if (!result.canceled && result.assets[0]) {
      setPhoto(result.assets[0].uri);
    }
  };

  const handleSubmit = async () => {
    if (!selectedType) {
      Alert.alert('Select Type', 'Please select an incident type');
      return;
    }

    if (!location) {
      Alert.alert('No Location', 'Could not determine your location');
      return;
    }

    setSubmitting(true);
    try {
      await incidentService.reportIncident({
        type: selectedType,
        description: description.trim() || undefined,
        latitude: location.latitude,
        longitude: location.longitude,
        media_url: photo || undefined, // In production, upload photo first
      });

      Alert.alert('✅ Report Submitted', 'Thank you for helping the community!', [
        { text: 'OK', onPress: () => {
          resetForm();
          onSuccess?.();
          onClose();
        }}
      ]);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to submit report');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setSelectedType(null);
    setDescription('');
    setPhoto(null);
  };

  const userTrust = user?.trust_score || 0;

  return (
    <Modal visible={visible} animationType="slide" transparent>
      <KeyboardAvoidingView 
        style={styles.overlay}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View style={styles.container}>
          <View style={styles.header}>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
              <Text style={styles.closeBtnText}>✕</Text>
            </TouchableOpacity>
            <Text style={styles.title}>📝 Report Incident</Text>
            <View style={{ width: 40 }} />
          </View>

          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            {/* Location */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>📍 Location</Text>
              <View style={styles.locationBox}>
                <Text style={styles.locationText}>{locationName}</Text>
                <TouchableOpacity onPress={getLocation}>
                  <Text style={styles.refreshBtn}>🔄</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Incident Type */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>What's happening?</Text>
              <View style={styles.typesGrid}>
                {INCIDENT_TYPES.map((type) => {
                  const isLocked = type.requiresTrust && userTrust < type.requiresTrust;
                  const isSelected = selectedType === type.id;
                  
                  if (isLocked) return null; // Hide locked types
                  
                  return (
                    <TouchableOpacity
                      key={type.id}
                      style={[styles.typeCard, isSelected && styles.typeCardSelected]}
                      onPress={() => setSelectedType(type.id)}
                    >
                      <Text style={styles.typeIcon}>{type.icon}</Text>
                      <Text style={[styles.typeLabel, isSelected && styles.typeLabelSelected]}>
                        {type.label}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>

            {/* Description */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Details (optional)</Text>
              <TextInput
                style={styles.descriptionInput}
                placeholder="What details can help others? E.g., 'About 5 officers, checking documents'"
                placeholderTextColor={COLORS.textDim}
                value={description}
                onChangeText={setDescription}
                multiline
                maxLength={500}
              />
              <Text style={styles.charCount}>{description.length}/500</Text>
            </View>

            {/* Photo */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>📷 Add Photo (optional)</Text>
              {photo ? (
                <View style={styles.photoPreview}>
                  <Image source={{ uri: photo }} style={styles.previewImage} />
                  <TouchableOpacity 
                    style={styles.removePhotoBtn}
                    onPress={() => setPhoto(null)}
                  >
                    <Text style={styles.removePhotoText}>✕</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <View style={styles.photoButtons}>
                  <TouchableOpacity style={styles.photoBtn} onPress={takePhoto}>
                    <Text style={styles.photoBtnIcon}>📸</Text>
                    <Text style={styles.photoBtnText}>Camera</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.photoBtn} onPress={pickImage}>
                    <Text style={styles.photoBtnIcon}>🖼️</Text>
                    <Text style={styles.photoBtnText}>Gallery</Text>
                  </TouchableOpacity>
                </View>
              )}
            </View>

            {/* Submit */}
            <TouchableOpacity 
              style={[styles.submitBtn, (!selectedType || submitting) && styles.submitBtnDisabled]}
              onPress={handleSubmit}
              disabled={!selectedType || submitting}
            >
              {submitting ? (
                <ActivityIndicator color={COLORS.background} />
              ) : (
                <Text style={styles.submitBtnText}>Submit Report</Text>
              )}
            </TouchableOpacity>

            <View style={{ height: 40 }} />
          </ScrollView>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  container: {
    backgroundColor: COLORS.card,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '90%',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  closeBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeBtnText: {
    fontSize: 20,
    color: COLORS.textDim,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  content: {
    padding: 20,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 12,
  },
  locationBox: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: COLORS.background,
    padding: 14,
    borderRadius: 12,
  },
  locationText: {
    flex: 1,
    color: COLORS.text,
    fontSize: 14,
  },
  refreshBtn: {
    fontSize: 18,
    marginLeft: 10,
  },
  typesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  typeCard: {
    width: '30%',
    backgroundColor: COLORS.background,
    padding: 12,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  typeCardSelected: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(2, 221, 237, 0.1)',
  },
  typeIcon: {
    fontSize: 28,
    marginBottom: 6,
  },
  typeLabel: {
    fontSize: 12,
    color: COLORS.textDim,
    textAlign: 'center',
  },
  typeLabelSelected: {
    color: COLORS.primary,
    fontWeight: '600',
  },
  descriptionInput: {
    backgroundColor: COLORS.background,
    borderRadius: 12,
    padding: 14,
    color: COLORS.text,
    fontSize: 14,
    minHeight: 100,
    textAlignVertical: 'top',
  },
  charCount: {
    textAlign: 'right',
    fontSize: 11,
    color: COLORS.textDim,
    marginTop: 4,
  },
  photoButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  photoBtn: {
    flex: 1,
    backgroundColor: COLORS.background,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
  },
  photoBtnIcon: {
    fontSize: 28,
    marginBottom: 6,
  },
  photoBtnText: {
    fontSize: 13,
    color: COLORS.textDim,
  },
  photoPreview: {
    position: 'relative',
    borderRadius: 12,
    overflow: 'hidden',
  },
  previewImage: {
    width: '100%',
    height: 180,
    borderRadius: 12,
  },
  removePhotoBtn: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: 'rgba(0,0,0,0.6)',
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removePhotoText: {
    color: 'white',
    fontSize: 16,
  },
  submitBtn: {
    backgroundColor: COLORS.primary,
    padding: 16,
    borderRadius: 14,
    alignItems: 'center',
  },
  submitBtnDisabled: {
    opacity: 0.5,
  },
  submitBtnText: {
    color: COLORS.background,
    fontSize: 16,
    fontWeight: 'bold',
  },
});
