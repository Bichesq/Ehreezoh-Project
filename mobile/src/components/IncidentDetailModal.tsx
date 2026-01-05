import React, { useState } from 'react';
import { Modal, View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Incident } from '../services/incident';
import IncidentVerificationButtons from './IncidentVerificationButtons';
import ThanksButton from './ThanksButton';
import IncidentComments from './IncidentComments';
import { useAuth } from '../context/AuthContext';
import { COLORS } from '../constants/colors';

interface IncidentDetailModalProps {
  incident: Incident | null;
  visible: boolean;
  onClose: () => void;
  onVerified?: () => void;
}

export default function IncidentDetailModal({ 
  incident, 
  visible, 
  onClose,
  onVerified 
}: IncidentDetailModalProps) {
  const { user } = useAuth();
  
  if (!incident) return null;

  const getTypeInfo = (type: string) => {
    switch (type) {
      case 'accident': return { icon: '💥', label: 'Accident', color: '#ef4444' };
      case 'police': return { icon: '👮', label: 'Police', color: '#3b82f6' };
      case 'traffic': return { icon: '🐢', label: 'Traffic Jam', color: '#f59e0b' };
      case 'roadblock': return { icon: '⛔', label: 'Roadblock', color: '#ef4444' };
      default: return { icon: '⚠️', label: type, color: '#f59e0b' };
    }
  };

  const typeInfo = getTypeInfo(incident.type);
  const timeAgo = getTimeAgo(incident.created_at);

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.overlay}>
        <View style={styles.container}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeText}>✕</Text>
          </TouchableOpacity>

          <ScrollView style={styles.scrollContent} showsVerticalScrollIndicator={false}>
            <View style={styles.header}>
              <View style={[styles.iconContainer, { backgroundColor: typeInfo.color + '20' }]}>
                <Text style={styles.icon}>{typeInfo.icon}</Text>
              </View>
              <View style={styles.headerText}>
                <Text style={styles.title}>{typeInfo.label}</Text>
                <Text style={styles.timeText}>{timeAgo}</Text>
              </View>
            </View>

            {incident.description && (
              <View style={styles.descriptionBox}>
                <Text style={styles.descriptionText}>{incident.description}</Text>
              </View>
            )}

            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{incident.confirmations || 0}</Text>
                <Text style={styles.statLabel}>Confirmations</Text>
              </View>
              {incident.is_verified && (
                <View style={styles.verifiedBadge}>
                  <Text style={styles.verifiedText}>✅ Verified</Text>
                </View>
              )}
            </View>

            <IncidentVerificationButtons 
              incidentId={incident.id} 
              onVerified={() => {
                onVerified?.();
              }}
            />

            {/* Thanks Button */}
            <ThanksButton 
              incidentId={incident.id}
              currentUserId={user?.id}
            />

            {/* Comments Section */}
            <IncidentComments incidentId={incident.id} />
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

function getTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${Math.floor(diffHours / 24)}d ago`;
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
    paddingBottom: 40,
    maxHeight: '85%',
  },
  scrollContent: {
    paddingBottom: 20,
  },
  closeButton: {
    position: 'absolute',
    top: 16,
    right: 16,
    padding: 8,
    zIndex: 10,
  },
  closeText: {
    fontSize: 20,
    color: COLORS.textDim,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  icon: {
    fontSize: 28,
  },
  headerText: {
    flex: 1,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  timeText: {
    fontSize: 14,
    color: COLORS.textDim,
    marginTop: 4,
  },
  descriptionBox: {
    backgroundColor: COLORS.background,
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  descriptionText: {
    fontSize: 14,
    color: COLORS.text,
    lineHeight: 20,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    gap: 16,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  statLabel: {
    fontSize: 12,
    color: COLORS.textDim,
  },
  verifiedBadge: {
    backgroundColor: 'rgba(34, 197, 94, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  verifiedText: {
    color: '#22c55e',
    fontWeight: '600',
    fontSize: 14,
  },
});
