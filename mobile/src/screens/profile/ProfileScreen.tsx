import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Image, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/auth';
import { StatusBar } from 'expo-status-bar';
import { gamificationService, GamificationStats } from '../../services/gamification';
import { COLORS } from '../../constants/colors';

export default function ProfileScreen() {
  const { user, signOut, setUser } = useAuth(); // Assuming setUser is exposed in context, if not we'll rely on response
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [photoUrl, setPhotoUrl] = useState(user?.profile_photo_url || '');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<GamificationStats | null>(null);
  const router = useRouter();

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await gamificationService.getMyStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load gamification stats:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const updatedUser = await authService.updateProfile({
        full_name: fullName,
        email: email,
        profile_photo_url: photoUrl
      });
      
      // Update local storage and context if possible (simplified here)
      if (setUser) {
          setUser(updatedUser);
      }
      
      Alert.alert('Success', 'Profile updated!');
    } catch (error) {
      console.error('Update failed:', error);
      Alert.alert('Error', 'Failed to update profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure?', [
      { text: 'Cancel', style: 'cancel' },
      { 
        text: 'Logout', 
        style: 'destructive', 
        onPress: async () => {
             await signOut();
             router.replace('/'); 
        } 
      }
    ]);
  };

  return (
    <View style={styles.container}>
      <StatusBar style="dark" />
      <View style={styles.header}>
        <Text style={styles.title}>My Profile</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.avatarContainer}>
            <View style={styles.avatar}>
                {photoUrl ? (
                    <Image source={{ uri: photoUrl }} style={styles.avatarImage} />
                ) : (
                    <Text style={styles.avatarPlaceholder}>{fullName?.charAt(0) || '?'}</Text>
                )}
            </View>
            <TouchableOpacity onPress={() => Alert.alert("Coming Soon", "Image upload not implemented yet")}>
                <Text style={styles.changePhotoText}>Change Photo</Text>
            </TouchableOpacity>
        </View>



        {/* Gamification Card */}
        <View style={styles.statsCard}>
            <View style={styles.statsHeader}>
              <Text style={styles.sectionTitle}>🏆 Community Impact</Text>
              <TouchableOpacity onPress={() => router.push('/community/leaderboard')}>
                <Text style={styles.viewLeaderboardLink}>View Leaderboard →</Text>
              </TouchableOpacity>
            </View>
            
            {/* Trust Level Badge & Progress */}
            {stats?.trust_level && (
              <View style={styles.trustBadgeContainer}>
                <View style={styles.trustHeader}>
                    <Text style={styles.trustIcon}>{stats.trust_icon || '🌱'}</Text>
                    <View style={{flex:1, marginLeft: 10}}>
                        <Text style={styles.trustLevel}>{stats.trust_level}</Text>
                        <Text style={styles.trustScoreText}>Trust Score: {stats.trust_score ?? 0}</Text>
                    </View>
                </View>
                
                {stats.next_level_score ? (
                    <View style={styles.progressBarContainer}>
                        <View style={styles.progressBarBg}>
                            <View style={[
                                styles.progressBarFill, 
                                { width: `${Math.min(100, Math.max(5, (stats.trust_score / stats.next_level_score) * 100))}%` } 
                            ]} />
                        </View>
                        <Text style={styles.progressText}>
                            {stats.trust_score} / {stats.next_level_score} to next level
                        </Text>
                    </View>
                ) : (
                    <Text style={styles.maxLevelText}>Maximum Level Reached! 👑</Text>
                )}
              </View>
            )}
            
            <View style={styles.statsRow}>
                <View style={styles.statItem}>
                    <Text style={styles.statValue}>{stats?.points ?? user?.points ?? 0}</Text>
                    <Text style={styles.statLabel}>Points</Text>
                </View>
                <View style={[styles.statItem, styles.statBorder]}>
                    <Text style={styles.statValue}>{stats?.total_reports ?? user?.total_reports ?? 0}</Text>
                    <Text style={styles.statLabel}>Reports</Text>
                </View>
                <View style={styles.statItem}>
                    <Text style={styles.statValue}>{stats?.badges ? stats.badges.filter(b => b.is_earned).length : 0}</Text>
                    <Text style={styles.statLabel}>Badges</Text>
                </View>
            </View>
            
            {/* Streak Display */}
            {(stats?.current_streak ?? 0) > 0 && (
              <View style={styles.streakContainer}>
                <Text style={styles.streakText}>🔥 {stats?.current_streak} day streak</Text>
              </View>
            )}
            
            {/* Badges Grid */}
            <View style={styles.badgesSection}>
                <Text style={styles.sectionSubtitle}>Badges</Text>
                {stats?.badges && stats.badges.length > 0 ? (
                    <View style={styles.badgeList}>
                        {stats.badges.map((b, i) => (
                            <TouchableOpacity 
                                key={i} 
                                style={[styles.badgeItem, !b.is_earned && styles.badgeLocked]}
                                onPress={() => {
                                    Alert.alert(
                                        b.name,
                                        `${b.description}\n\n${b.is_earned ? `Earned on ${new Date(b.earned_at!).toLocaleDateString()}` : 'Locked'}`
                                    );
                                }}
                            >
                                <Text style={[styles.badgeIconText, !b.is_earned && { opacity: 0.3 }]}>
                                    {b.icon || '🏅'}
                                </Text>
                                <Text style={styles.badgeName} numberOfLines={1}>{b.name}</Text>
                                {!b.is_earned && <Text style={styles.lockIcon}>🔒</Text>}
                            </TouchableOpacity>
                        ))}
                    </View>
                ) : (
                    <Text style={styles.noBadgesText}>No badges available yet.</Text>
                )}
            </View>
        </View>

        <View style={styles.form}>
            <Text style={styles.label}>Full Name</Text>
            <TextInput 
                style={styles.input} 
                value={fullName}
                onChangeText={setFullName}
                placeholder="Enter your name"
            />

            <Text style={styles.label}>Email (Optional)</Text>
             <TextInput 
                style={styles.input} 
                value={email}
                onChangeText={setEmail}
                placeholder="Enter your email"
                keyboardType="email-address"
                autoCapitalize="none"
            />
            
             <Text style={styles.label}>Phone Number</Text>
             <TextInput 
                style={[styles.input, styles.disabledInput]} 
                value={user?.phone_number}
                editable={false}
            />
        </View>

        <TouchableOpacity style={styles.saveButton} onPress={handleSave} disabled={loading}>
            {loading ? <ActivityIndicator color="white" /> : <Text style={styles.saveButtonText}>Save Changes</Text>}
        </TouchableOpacity>

        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Text style={styles.logoutButtonText}>Log Out</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  title: {
      fontSize: 20,
      fontWeight: 'bold',
  },
  backButton: {
      padding: 10,
  },
  backButtonText: {
      fontSize: 16,
      color: '#007AFF',
  },
  content: {
      padding: 20,
  },
  avatarContainer: {
      alignItems: 'center',
      marginBottom: 30,
  },
  avatar: {
      width: 100,
      height: 100,
      borderRadius: 50,
      backgroundColor: '#f0f0f0',
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: 10,
      overflow: 'hidden',
  },
  avatarImage: {
      width: '100%',
      height: '100%',
  },
  avatarPlaceholder: {
      fontSize: 40,
      color: '#999',
  },
  changePhotoText: {
      color: '#007AFF',
      fontSize: 16,
  },
  form: {
      marginBottom: 30,
  },
  label: {
      fontSize: 14,
      color: '#666',
      marginBottom: 5,
      marginTop: 15,
  },
  input: {
      backgroundColor: '#f9f9f9',
      padding: 15,
      borderRadius: 10,
      borderWidth: 1,
      borderColor: '#eee',
      fontSize: 16,
  },
  disabledInput: {
      color: '#999',
      backgroundColor: '#f0f0f0',
  },
  saveButton: {
      backgroundColor: '#000',
      padding: 18,
      borderRadius: 12,
      alignItems: 'center',
      marginBottom: 15,
  },
  saveButtonText: {
      color: 'white',
      fontWeight: 'bold',
      fontSize: 16,
  },
  logoutButton: {
      backgroundColor: '#fee',
      padding: 18,
      borderRadius: 12,
      alignItems: 'center',
  },
  logoutButtonText: {
      color: '#d00',
      fontWeight: 'bold',
      fontSize: 16,
  },
  // Gamification Styles
  statsCard: {
      backgroundColor: '#f8f9fa',
      padding: 20,
      borderRadius: 16,
      marginBottom: 30,
      borderWidth: 1,
      borderColor: '#e9ecef',
  },
  sectionTitle: {
      fontSize: 18,
      fontWeight: 'bold',
      marginBottom: 15,
      color: '#333',
  },
  statsRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginBottom: 20,
  },
  statItem: {
      flex: 1,
      alignItems: 'center',
  },
  statBorder: {
      borderLeftWidth: 1,
      borderRightWidth: 1,
      borderColor: '#dee2e6',
  },
  statValue: {
      fontSize: 24,
      fontWeight: 'bold',
      color: COLORS.primary,
  },
  statLabel: {
      fontSize: 12,
      color: '#6c757d',
      marginTop: 4,
  },
  // Removed duplicate badge styles

  // New community styles
  statsHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 15,
  },
  viewLeaderboardLink: {
      fontSize: 14,
      color: COLORS.primary,
      fontWeight: '600',
  },
  trustBadgeContainer: {
      backgroundColor: 'rgba(2, 221, 237, 0.1)',
      padding: 16,
      borderRadius: 16,
      marginBottom: 20,
  },
  trustHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 12,
  },
  trustIcon: {
      fontSize: 32,
  },
  trustLevel: {
      fontSize: 20,
      fontWeight: 'bold',
      color: '#333',
  },
  trustScoreText: {
      fontSize: 14,
      color: '#6c757d',
  },
  progressBarContainer: {
      marginTop: 8,
  },
  progressBarBg: {
      height: 8,
      backgroundColor: 'rgba(0,0,0,0.1)',
      borderRadius: 4,
      overflow: 'hidden',
  },
  progressBarFill: {
      height: '100%',
      backgroundColor: COLORS.primary,
      borderRadius: 4,
  },
  progressText: {
      fontSize: 12,
      color: '#6c757d',
      marginTop: 4,
      textAlign: 'right',
  },
  maxLevelText: {
      fontSize: 14,
      color: COLORS.primary,
      fontWeight: 'bold',
      textAlign: 'center',
      marginTop: 8,
  },
  streakContainer: {
      backgroundColor: 'rgba(255, 165, 0, 0.1)',
      padding: 10,
      borderRadius: 8,
      marginBottom: 15,
      alignItems: 'center',
  },
  streakText: {
      fontSize: 14,
      fontWeight: '600',
      color: '#f59e0b',
  },
  badgesSection: {
      borderTopWidth: 1,
      borderColor: '#eee',
      paddingTop: 15,
  },
  sectionSubtitle: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 12,
      color: '#333',
  },
  badgeList: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 12,
  },
  badgeItem: {
      alignItems: 'center',
      width: '30%',
      marginBottom: 16,
      padding: 8,
      borderRadius: 8,
      backgroundColor: '#fff',
      borderWidth: 1,
      borderColor: '#eee',
  },
  badgeLocked: {
      backgroundColor: '#f8f9fa',
      borderColor: '#e9ecef',
      opacity: 0.7,
  },
  badgeIconText: {
      fontSize: 28,
      marginBottom: 4,
  },
  badgeName: {
      fontSize: 11,
      textAlign: 'center',
      color: '#333',
      fontWeight: '500',
  },
  lockIcon: {
      position: 'absolute',
      right: 4,
      top: 4,
      fontSize: 10,
  },
  noBadgesText: {
      fontSize: 14,
      color: '#999',
      fontStyle: 'italic',
      textAlign: 'center',
      marginTop: 10,
  }
});
