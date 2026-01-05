import React from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { COLORS } from '../constants/colors';

interface ViewToggleProps {
  activeView: 'map' | 'feed';
  onChangeView: (view: 'map' | 'feed') => void;
}

export default function ViewToggle({ activeView, onChangeView }: ViewToggleProps) {
  // Position toggle higher on Map (above "Where to?" sheet), lower on Feed
  const bottomPosition = activeView === 'map' ? 190 : 30;

  return (
    <View style={[styles.container, { bottom: bottomPosition }]}>
      <View style={styles.toggleWrapper}>
        <TouchableOpacity
          style={[styles.tab, activeView === 'map' && styles.activeTab]}
          onPress={() => onChangeView('map')}
        >
          <Text style={[styles.tabIcon, activeView === 'map' && styles.activeTabText]}>🗺️</Text>
          <Text style={[styles.tabText, activeView === 'map' && styles.activeTabText]}>Map</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeView === 'feed' && styles.activeTab]}
          onPress={() => onChangeView('feed')}
        >
          <Text style={[styles.tabIcon, activeView === 'feed' && styles.activeTabText]}>📱</Text>
          <Text style={[styles.tabText, activeView === 'feed' && styles.activeTabText]}>Feed</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    left: 0,
    right: 0,
    alignItems: 'center',
    zIndex: 50,
  },
  toggleWrapper: {
    flexDirection: 'row',
    backgroundColor: COLORS.card,
    borderRadius: 25,
    padding: 4,
    borderWidth: 1,
    borderColor: COLORS.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  tab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 22,
    gap: 6,
  },
  activeTab: {
    backgroundColor: COLORS.primary,
  },
  tabIcon: {
    fontSize: 16,
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.textDim,
  },
  activeTabText: {
    color: COLORS.background,
  },
});
