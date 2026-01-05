import React from 'react';
import { Share, Alert, Platform } from 'react-native';

interface Achievement {
  type: 'badge' | 'milestone' | 'thanks' | 'level_up';
  title: string;
  description: string;
  value?: number;
  icon?: string;
}

export const shareAchievement = async (achievement: Achievement, appName: string = 'Ehreezoh'): Promise<boolean> => {
  try {
    let message = '';
    
    switch (achievement.type) {
      case 'badge':
        message = `${achievement.icon || '🏅'} I just earned the "${achievement.title}" badge on ${appName}! ${achievement.description}`;
        break;
      case 'milestone':
        message = `🎯 Milestone reached on ${appName}! ${achievement.title}: ${achievement.value} ${achievement.description}`;
        break;
      case 'thanks':
        message = `💙 ${achievement.value} people have thanked me on ${appName} for helping the community! #CommunityHero`;
        break;
      case 'level_up':
        message = `🚀 I leveled up to "${achievement.title}" on ${appName}! ${achievement.description} Join me in making our roads safer.`;
        break;
      default:
        message = `${achievement.icon || '🌟'} ${achievement.title} - ${achievement.description} via ${appName}`;
    }

    // Add app link placeholder
    message += '\n\nDownload Ehreezoh: https://ehreezoh.app';

    const result = await Share.share({
      message,
      title: `${appName} Achievement`,
    });

    if (result.action === Share.sharedAction) {
      return true;
    }
    return false;
  } catch (error: any) {
    Alert.alert('Share Failed', error.message || 'Could not share achievement');
    return false;
  }
};

// Quick share methods
export const shareBadge = (badgeName: string, badgeIcon: string, description: string) => 
  shareAchievement({
    type: 'badge',
    title: badgeName,
    description,
    icon: badgeIcon
  });

export const shareMilestone = (milestoneName: string, value: number, unit: string) => 
  shareAchievement({
    type: 'milestone',
    title: milestoneName,
    description: unit,
    value
  });

export const shareThanks = (thanksCount: number) => 
  shareAchievement({
    type: 'thanks',
    title: 'Thanks Received',
    description: 'thanks from the community',
    value: thanksCount
  });

export const shareLevelUp = (levelName: string, levelDescription: string, levelIcon: string) => 
  shareAchievement({
    type: 'level_up',
    title: levelName,
    description: levelDescription,
    icon: levelIcon
  });
