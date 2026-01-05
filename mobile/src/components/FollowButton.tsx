import React, { useState, useEffect } from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { socialService } from '../services/social';
import { COLORS } from '../constants/colors';

interface FollowButtonProps {
  userId: string;
  currentUserId?: string;
  compact?: boolean;
  onFollowChange?: (isFollowing: boolean) => void;
}

export default function FollowButton({ 
  userId, 
  currentUserId, 
  compact = false,
  onFollowChange 
}: FollowButtonProps) {
  const [loading, setLoading] = useState(false);
  const [isFollowing, setIsFollowing] = useState(false);
  const [checked, setChecked] = useState(false);

  // Don't show for own profile
  if (currentUserId && userId === currentUserId) {
    return null;
  }

  useEffect(() => {
    checkFollowStatus();
  }, [userId]);

  const checkFollowStatus = async () => {
    try {
      const status = await socialService.getFollowStatus(userId);
      setIsFollowing(status.is_following);
    } catch (error) {
      // Silent fail
    } finally {
      setChecked(true);
    }
  };

  const handleToggle = async () => {
    if (loading) return;

    setLoading(true);
    try {
      if (isFollowing) {
        await socialService.unfollowUser(userId);
        setIsFollowing(false);
        onFollowChange?.(false);
      } else {
        await socialService.followUser(userId);
        setIsFollowing(true);
        onFollowChange?.(true);
      }
    } catch (error: any) {
      console.error('Follow toggle failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!checked) return null;

  return (
    <TouchableOpacity 
      style={[
        styles.button, 
        isFollowing && styles.followingButton,
        compact && styles.buttonCompact
      ]}
      onPress={handleToggle}
      disabled={loading}
    >
      {loading ? (
        <ActivityIndicator size="small" color={isFollowing ? COLORS.textDim : COLORS.background} />
      ) : (
        <Text style={[
          styles.text, 
          isFollowing && styles.followingText,
          compact && styles.textCompact
        ]}>
          {isFollowing ? '✓ Following' : '+ Follow'}
        </Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: COLORS.primary,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 90,
  },
  buttonCompact: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    minWidth: 70,
  },
  followingButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  text: {
    color: COLORS.background,
    fontWeight: '600',
    fontSize: 14,
  },
  textCompact: {
    fontSize: 12,
  },
  followingText: {
    color: COLORS.textDim,
  },
});
