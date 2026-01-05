import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  TouchableOpacity, 
  ActivityIndicator,
  Image,
  RefreshControl
} from 'react-native';
import { useRouter } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { COLORS } from '../../constants/colors';

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  full_name: string;
  points: number;
  trust_score: number;
  total_reports: number;
  profile_photo_url?: string;
  is_current_user?: boolean;
}

interface MyRank {
  rank: number;
  total_contributors: number;
  points: number;
  trust_score: number;
  percentile: number;
}

export default function LeaderboardScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [myRank, setMyRank] = useState<MyRank | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [leaderboardRes, rankRes] = await Promise.all([
        api.get('/community/leaderboard'),
        api.get('/community/my-rank')
      ]);
      setLeaderboard(leaderboardRes.data);
      setMyRank(rankRes.data);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const getRankEmoji = (rank: number) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  const getTrustIcon = (score: number) => {
    if (score >= 500) return '👑';
    if (score >= 300) return '🦁';
    if (score >= 150) return '🛡️';
    if (score >= 50) return '✅';
    return '🌱';
  };

  const renderItem = ({ item }: { item: LeaderboardEntry }) => (
    <View style={[
      styles.entryCard,
      item.is_current_user && styles.currentUserCard
    ]}>
      <View style={styles.rankContainer}>
        <Text style={styles.rankText}>{getRankEmoji(item.rank)}</Text>
      </View>
      
      <View style={styles.avatarContainer}>
        {item.profile_photo_url ? (
          <Image source={{ uri: item.profile_photo_url }} style={styles.avatar} />
        ) : (
          <View style={styles.avatarPlaceholder}>
            <Text style={styles.avatarText}>{item.full_name?.charAt(0) || '?'}</Text>
          </View>
        )}
      </View>
      
      <View style={styles.infoContainer}>
        <Text style={styles.name} numberOfLines={1}>
          {item.full_name || 'Anonymous'}
          {item.is_current_user && ' (You)'}
        </Text>
        <View style={styles.statsRow}>
          <Text style={styles.statText}>🪶 {item.total_reports} reports</Text>
          <Text style={styles.statText}>{getTrustIcon(item.trust_score)} {item.trust_score}</Text>
        </View>
      </View>
      
      <View style={styles.pointsContainer}>
        <Text style={styles.pointsValue}>{item.points}</Text>
        <Text style={styles.pointsLabel}>pts</Text>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Loading leaderboard...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🏆 Leaderboard</Text>
      </View>

      {/* My Rank Card */}
      {myRank && (
        <View style={styles.myRankCard}>
          <View style={styles.myRankRow}>
            <View style={styles.myRankItem}>
              <Text style={styles.myRankValue}>#{myRank.rank}</Text>
              <Text style={styles.myRankLabel}>Your Rank</Text>
            </View>
            <View style={styles.myRankDivider} />
            <View style={styles.myRankItem}>
              <Text style={styles.myRankValue}>{myRank.points}</Text>
              <Text style={styles.myRankLabel}>Points</Text>
            </View>
            <View style={styles.myRankDivider} />
            <View style={styles.myRankItem}>
              <Text style={styles.myRankValue}>Top {myRank.percentile}%</Text>
              <Text style={styles.myRankLabel}>Percentile</Text>
            </View>
          </View>
        </View>
      )}

      {/* Leaderboard List */}
      <FlatList
        data={leaderboard}
        renderItem={renderItem}
        keyExtractor={(item) => item.user_id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl 
            refreshing={refreshing} 
            onRefresh={onRefresh}
            tintColor={COLORS.primary}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>🏅</Text>
            <Text style={styles.emptyText}>No contributors yet</Text>
            <Text style={styles.emptySubtext}>Be the first to report an incident!</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  loadingText: {
    marginTop: 12,
    color: COLORS.textDim,
    fontSize: 16,
  },
  header: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 16,
    backgroundColor: COLORS.card,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    fontSize: 16,
    color: COLORS.primary,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  myRankCard: {
    backgroundColor: COLORS.card,
    margin: 16,
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: COLORS.primary,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  myRankRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  myRankItem: {
    alignItems: 'center',
    flex: 1,
  },
  myRankValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  myRankLabel: {
    fontSize: 12,
    color: COLORS.textDim,
    marginTop: 4,
  },
  myRankDivider: {
    width: 1,
    height: 40,
    backgroundColor: COLORS.border,
  },
  listContent: {
    padding: 16,
    paddingTop: 0,
  },
  entryCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  currentUserCard: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(2, 221, 237, 0.1)',
  },
  rankContainer: {
    width: 40,
    alignItems: 'center',
  },
  rankText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  avatarContainer: {
    marginRight: 12,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
  },
  avatarPlaceholder: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: COLORS.border,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.textDim,
  },
  infoContainer: {
    flex: 1,
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 4,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
  },
  statText: {
    fontSize: 12,
    color: COLORS.textDim,
  },
  pointsContainer: {
    alignItems: 'center',
    paddingLeft: 12,
  },
  pointsValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  pointsLabel: {
    fontSize: 10,
    color: COLORS.textDim,
  },
  emptyState: {
    alignItems: 'center',
    paddingTop: 60,
  },
  emptyIcon: {
    fontSize: 60,
    marginBottom: 16,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: COLORS.textDim,
  },
});
