import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import MapScreen from './MapScreen';
import CommunityFeedScreen from '../community/CommunityFeedScreen';
import ViewToggle from '../../components/ViewToggle';
import { COLORS } from '../../constants/colors';

export default function HomeScreen() {
  const [activeView, setActiveView] = useState<'map' | 'feed'>('map');

  return (
    <View style={styles.container}>
      {activeView === 'map' ? (
        <MapScreen />
      ) : (
        <CommunityFeedScreen />
      )}
      
      <ViewToggle 
        activeView={activeView} 
        onChangeView={setActiveView} 
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
});
