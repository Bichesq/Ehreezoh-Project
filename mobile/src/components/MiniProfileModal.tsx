import React, { useState, useEffect } from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { api } from '../services/api';
import { socialService } from '../services/social';
import { COLORS } from '../constants/colors';

interface MiniProfileModalProps {
  userId: string | null;
  visible: boolean;
  onClose: () => void;
  currentUserId?: string;
}

interface ProfileData {
  id: string;
  name: string;
  profile_photo_url?: string;
  trust_score: number;
  trust_level: { name: string; color: string; icon: string };
  badges: Array<{ name: string; icon: string; tier: number }>;
  stats: {
    incidents_reported: number;
    thanks_received: number;
    comments_made: number;
    people_helped: number;
  };
  social: {
    followers: number;
    following: number;
    is_following: boolean;
  };
  is_self: boolean;
  member_since?: string;
}

export default function MiniProfileModal({
  userId,
  visible,
  onClose,
  currentUserId
}: MiniProfileModalProps) {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [isFollowing, setIsFollowing] = useState(false);
  const [followLoading, setFollowLoading] = useState(false);

  useEffect(() => {
    if (visible && userId) {
      loadProfile();
    }
  }, [visible, userId]);

  const loadProfile = async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const response = await api.get(`/profiles/${userId}`);
      setProfile(response.data);
      setIsFollowing(response.data.social.is_following);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async () => {
    if (!userId || followLoading) return;
    setFollowLoading(true);
    try {
      if (isFollowing) {
        await socialService.unfollowUser(userId);
        setIsFollowing(false);
      } else {
        await socialService.followUser(userId);
        setIsFollowing(true);
      }
    } catch (error) {
      console.error('Follow action failed:', error);
    } finally {
      setFollowLoading(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  };

  if (!visible) return null;

  return (
    <Modal visible={visible} transparent animationType="fade">
      <TouchableOpacity 
        style={styles.overlay} 
        activeOpacity={1} 
        onPress={onClose}
      >
        <TouchableOpacity 
          style={styles.container} 
          activeOpacity={1}
          onPress={(e) => e.stopPropagation()}
        >
          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={COLORS.primary} />
            </View>
          ) : profile ? (
            <ScrollView showsVerticalScrollIndicator={false}>
              {/* Close button */}
              <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
                <Text style={styles.closeBtnText}>✕</Text>
              </TouchableOpacity>

              {/* Avatar & Name */}
              <View style={styles.header}>
                {profile.profile_photo_url ? (
                  <Image source={{ uri: profile.profile_photo_url }} style={styles.avatar} />
                ) : (
                  <View style={styles.avatarPlaceholder}>
                    <Text style={styles.avatarText}>{profile.name.charAt(0)}</Text>
                  </View>
                )}
                <Text style={styles.name}>{profile.name}</Text>
                
                {/* Trust Level Badge */}
                <View style={[styles.trustBadge, { borderColor: profile.trust_level.color }]}>
                  <Text style={styles.trustIcon}>{profile.trust_level.icon}</Text>
                  <Text style={[styles.trustName, { color: profile.trust_level.color }]}>
                    {profile.trust_level.name}
                  </Text>
                </View>
                
                <Text style={styles.memberSince}>
                  Member since {formatDate(profile.member_since)}
                </Text>
              </View>

              {/* Stats */}
              <View style={styles.statsRow}>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{profile.stats.incidents_reported}</Text>
                  <Text style={styles.statLabel}>Reports</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{profile.stats.thanks_received}</Text>
                  <Text style={styles.statLabel}>Thanks</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statValue}>{profile.stats.people_helped}</Text>
                  <Text style={styles.statLabel}>Helped</Text>
                </View>
              </View>

              {/* Followers/Following */}
              <View style={styles.socialRow}>
                <Text style={styles.socialText}>
                  <Text style={styles.socialNum}>{profile.social.followers}</Text> followers
                </Text>
                <Text style={styles.socialDot}>•</Text>
                <Text style={styles.socialText}>
                  <Text style={styles.socialNum}>{profile.social.following}</Text> following
                </Text>
              </View>

              {/* Badges */}
              {profile.badges.length > 0 && (
                <View style={styles.badgesSection}>
                  <Text style={styles.sectionTitle}>🏅 Badges</Text>
                  <View style={styles.badgesRow}>
                    {profile.badges.map((badge, index) => (
                      <View key={index} style={styles.badgeItem}>
                        <Text style={styles.badgeIcon}>{badge.icon}</Text>
                        <Text style={styles.badgeName}>{badge.name}</Text>
                      </View>
                    ))}
                  </View>
                </View>
              )}

              {/* Follow Button */}
              {!profile.is_self && (
                <TouchableOpacity 
                  style={[styles.followBtn, isFollowing && styles.followingBtn]}
                  onPress={handleFollow}
                  disabled={followLoading}
                >
                  {followLoading ? (
                    <ActivityIndicator size="small" color={isFollowing ? COLORS.textDim : COLORS.background} />
                  ) : (
                    <Text style={[styles.followBtnText, isFollowing && styles.followingBtnText]}>
                      {isFollowing ? '✓ Following' : '+ Follow'}
                    </Text>
                  )}
                </TouchableOpacity>
              )}
            </ScrollView>
          ) : (
            <Text style={styles.errorText}>Could not load profile</Text>
          )}
        </TouchableOpacity>
      </TouchableOpacity>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  container: {
    backgroundColor: COLORS.card,
    borderRadius: 24,
    padding: 24,
    width: '100%',
    maxWidth: 340,
    maxHeight: '80%',
  },
  loadingContainer: {
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeBtn: {
    position: 'absolute',
    top: 0,
    right: 0,
    padding: 8,
    zIndex: 10,
  },
  closeBtnText: {
    fontSize: 18,
    color: COLORS.textDim,
  },
  header: {
    alignItems: 'center',
    marginBottom: 20,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    marginBottom: 12,
  },
  avatarPlaceholder: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: COLORS.primary + '30',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  avatarText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  name: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 8,
  },
  trustBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 4,
    marginBottom: 8,
  },
  trustIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  trustName: {
    fontSize: 13,
    fontWeight: '600',
  },
  memberSince: {
    fontSize: 12,
    color: COLORS.textDim,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 16,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 12,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  statLabel: {
    fontSize: 12,
    color: COLORS.textDim,
    marginTop: 2,
  },
  socialRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  socialText: {
    fontSize: 14,
    color: COLORS.textDim,
  },
  socialNum: {
    fontWeight: 'bold',
    color: COLORS.text,
  },
  socialDot: {
    color: COLORS.textDim,
    marginHorizontal: 8,
  },
  badgesSection: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 10,
  },
  badgesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  badgeItem: {
    backgroundColor: COLORS.background,
    padding: 8,
    borderRadius: 10,
    alignItems: 'center',
    minWidth: 60,
  },
  badgeIcon: {
    fontSize: 20,
    marginBottom: 4,
  },
  badgeName: {
    fontSize: 10,
    color: COLORS.textDim,
    textAlign: 'center',
  },
  followBtn: {
    backgroundColor: COLORS.primary,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  followingBtn: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  followBtnText: {
    color: COLORS.background,
    fontWeight: '600',
    fontSize: 15,
  },
  followingBtnText: {
    color: COLORS.textDim,
  },
  errorText: {
    textAlign: 'center',
    color: COLORS.textDim,
    padding: 40,
  },
});
