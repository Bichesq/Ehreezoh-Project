import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import MapScreen from '../src/screens/home/MapScreen';
import CommunityFeedScreen from '../src/screens/community/CommunityFeedScreen';
import DriverHomeScreen from '../src/screens/driver/DriverHomeScreen';
import ViewToggle from '../src/components/ViewToggle';
import { useAuth } from '../src/context/AuthContext';
import { StatusBar } from 'expo-status-bar';
import { COLORS } from '../src/constants/colors';
import { SHADOWS } from '../src/constants/theme';

export default function HomeScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const [isDriverMode, setIsDriverMode] = useState(false);
  const [activeView, setActiveView] = useState<'map' | 'feed'>('map');

  // If user is not valid, the protected route logic will redirect them anyway
  if (!user) return null;

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Main Content */}
      {isDriverMode ? (
        <DriverHomeScreen />
      ) : (
        <>
          {activeView === 'map' ? <MapScreen /> : <CommunityFeedScreen />}
          <ViewToggle activeView={activeView} onChangeView={setActiveView} />
        </>
      )}

      {/* Role Switcher (Only visible to drivers) */}
      {user.is_driver && (
        <View style={styles.roleSwitchContainer}>
            <TouchableOpacity 
                style={[styles.roleButton, !isDriverMode && styles.activeRole]}
                onPress={() => setIsDriverMode(false)}
            >
                <Text style={[styles.roleText, !isDriverMode && styles.activeRoleText]}>Passenger</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
                style={[styles.roleButton, isDriverMode && styles.activeRole]}
                onPress={() => setIsDriverMode(true)}
            >
                <Text style={[styles.roleText, isDriverMode && styles.activeRoleText]}>Driver</Text>
            </TouchableOpacity>
        </View>
      )}

      {/* Report FAB - Only visible in Map Mode for Passengers/Drivers */}
      {!isDriverMode && activeView === 'map' && (
        <TouchableOpacity 
            style={styles.fab}
            onPress={() => router.push('/report')}
        >
            <Ionicons name="warning" size={28} color="#FFF" />
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  roleSwitchContainer: {
    position: 'absolute',
    top: 100,
    alignSelf: 'center',
    flexDirection: 'row',
    backgroundColor: COLORS.card,
    borderRadius: 25,
    padding: 4,
    ...SHADOWS.medium,
    borderWidth: 1,
    borderColor: COLORS.border,
    zIndex: 100, 
  },
  roleButton: {
    paddingVertical: 8,
    paddingHorizontal: 24,
    borderRadius: 20,
  },
  activeRole: {
    backgroundColor: COLORS.primary,
  },
  roleText: {
    fontWeight: 'bold',
    color: COLORS.textDim,
  },
  activeRoleText: {
    color: COLORS.background,
    fontWeight: 'bold',
  },
  fab: {
    position: 'absolute',
    bottom: 100,
    right: 20,
    backgroundColor: '#FF3B30',
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    ...SHADOWS.medium,
    elevation: 5,
  },
});
