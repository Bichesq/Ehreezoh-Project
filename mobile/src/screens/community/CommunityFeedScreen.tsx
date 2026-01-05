import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Image,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { useSocket } from '../../context/SocketContext';
import { COLORS } from '../../constants/colors';
import IncidentVerificationButtons from '../../components/IncidentVerificationButtons';
import ThanksButton from '../../components/ThanksButton';
import FollowButton from '../../components/FollowButton';
import EnhancedIncidentReport from '../../components/EnhancedIncidentReport';
import MiniProfileModal from '../../components/MiniProfileModal';

interface FeedItem {
  id: string;
  type: string;
  description?: string;
  latitude: number;
  longitude: number;
  media_url?: string;
  created_at: string;
  status: string;
  is_verified: boolean;
  confirmations: number;
  reporter: {
    id: string;
    name: string;
    profile_photo_url?: string;
    trust_score: number;
    trust_level: { name: string; icon: string };
    badge?: { name: string; icon: string };
  };
  verifications: {
    still_there: number;
    all_clear: number;
  };
  impact: {
    people_helped: number;
  };
}

export default function CommunityFeedScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const [items, setItems] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);

  const { socket } = useSocket();

  useEffect(() => {
    loadFeed(1, true);
  }, []);

  useEffect(() => {
    if (!socket) return;
    
    // Listen for vote updates
    const unsubscribe = socket.addListener((event: any) => {
        if (event.type === 'incident_verified') {
            const { incident_id, confirmations, verification_type } = event.data;
            
            setItems(prevItems => prevItems.map(item => {
                if (item.id === incident_id) {
                    return {
                        ...item,
                        confirmations: confirmations, // Update total confirmation score (often same as still_there count)
                        verifications: {
                            ...item.verifications,
                            still_there: verification_type === 'still_there' ? confirmations : item.verifications.still_there,
                            // Note: 'all_clear' logic might differ depending on backend implementation
                        }
                    };
                }
                return item;
            }));
        }
    });
    
    return () => {
       unsubscribe(); 
    };
  }, [socket]);

  const loadFeed = async (pageNum: number, reset: boolean = false) => {
    try {
      const response = await api.get('/incidents/feed', {
        params: { page: pageNum, limit: 15 }
      });
      const data = response.data;
      
      if (reset) {
        setItems(data.items);
      } else {
        setItems(prev => [...prev, ...data.items]);
      }
      setHasMore(data.has_more);
      setPage(pageNum);
    } catch (error) {
      console.error('Failed to load feed:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
      setLoadingMore(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadFeed(1, true);
  };

  const loadMore = () => {
    if (!hasMore || loadingMore) return;
    setLoadingMore(true);
    loadFeed(page + 1, false);
  };

  const getTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  const getTypeInfo = (type: string) => {
    switch (type.toLowerCase()) {
      case 'accident': return { icon: '💥', label: 'Accident', color: '#ef4444' };
      case 'police': return { icon: '👮', label: 'Police', color: '#3b82f6' };
      case 'checkpoint': return { icon: '🛑', label: 'Checkpoint', color: '#f59e0b' };
      case 'traffic': return { icon: '🐢', label: 'Traffic Jam', color: '#f59e0b' };
      case 'roadblock': return { icon: '⛔', label: 'Roadblock', color: '#ef4444' };
      case 'hazard': return { icon: '⚠️', label: 'Hazard', color: '#f59e0b' };
      default: return { icon: '⚠️', label: type, color: '#f59e0b' };
    }
  };

  const renderItem = useCallback(({ item }: { item: FeedItem }) => {
    const typeInfo = getTypeInfo(item.type);
    const timeAgo = getTimeAgo(item.created_at);

    return (
      <View style={styles.card}>
        {/* Reporter Header */}
        <View style={styles.cardHeader}>
          <View style={styles.reporterInfo}>
            {item.reporter.profile_photo_url ? (
              <Image 
                source={{ uri: item.reporter.profile_photo_url }} 
                style={styles.avatar}
              />
            ) : (
              <View style={styles.avatarPlaceholder}>
                <Text style={styles.avatarText}>
                  {item.reporter.name?.charAt(0) || '?'}
                </Text>
              </View>
            )}
            <View style={styles.reporterDetails}>
              <View style={styles.reporterNameRow}>
                {item.reporter.badge && (
                  <Text style={styles.badgeIcon}>{item.reporter.badge.icon}</Text>
                )}
                <TouchableOpacity onPress={() => setSelectedUserId(item.reporter.id)}>
                  <Text style={styles.reporterName}>{item.reporter.name}</Text>
                </TouchableOpacity>
              </View>
              <Text style={styles.timeText}>{timeAgo}</Text>
            </View>
          </View>
          <View style={styles.headerActions}>
            {item.reporter.id && item.reporter.id !== user?.id && (
              <FollowButton userId={item.reporter.id} currentUserId={user?.id} compact />
            )}
            {item.is_verified && (
              <View style={styles.verifiedBadge}>
                <Text style={styles.verifiedText}>✅ Verified</Text>
              </View>
            )}
          </View>
        </View>

        {/* Incident Type Banner */}
        <View style={[styles.typeBanner, { backgroundColor: typeInfo.color + '20' }]}>
          <Text style={styles.typeIcon}>{typeInfo.icon}</Text>
          <Text style={[styles.typeLabel, { color: typeInfo.color }]}>{typeInfo.label}</Text>
        </View>

        {/* Description */}
        {item.description && (
          <Text style={styles.description}>{item.description}</Text>
        )}

        {/* Media Preview (if any) */}
        {item.media_url && (
          <Image source={{ uri: item.media_url }} style={styles.mediaImage} />
        )}

        {/* Stats Row */}
        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Text style={styles.statValue}>👍 {item.verifications.still_there}</Text>
            <Text style={styles.statLabel}>Confirmed</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statValue}>✅ {item.verifications.all_clear}</Text>
            <Text style={styles.statLabel}>Clear</Text>
          </View>
          {item.impact.people_helped > 0 && (
            <View style={styles.stat}>
              <Text style={styles.statValue}>🛡️ {item.impact.people_helped}</Text>
              <Text style={styles.statLabel}>Helped</Text>
            </View>
          )}
        </View>

        {/* Verification Buttons */}
        <IncidentVerificationButtons 
          incidentId={item.id}
          onVerified={() => loadFeed(1, true)}
        />

        {/* Thanks Button */}
        <ThanksButton 
          incidentId={item.id}
          reporterId={item.reporter.id}
          currentUserId={user?.id}
        />

        {/* View on Map */}
        <TouchableOpacity 
          style={styles.mapButton}
          onPress={() => router.push(`/?lat=${item.latitude}&lng=${item.longitude}`)}
        >
          <Text style={styles.mapButtonText}>🗺️ View on Map</Text>
        </TouchableOpacity>
      </View>
    );
  }, []);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Loading feed...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>🔥 Live Feed</Text>
          <Text style={styles.subtitle}>What's happening nearby</Text>
        </View>
        <TouchableOpacity 
          style={styles.chatIconBtn}
          onPress={() => router.push('/community/chat')}
        >
          <Text style={styles.chatIcon}>💬</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={items}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={COLORS.primary}
          />
        }
        onEndReached={loadMore}
        onEndReachedThreshold={0.3}
        ListFooterComponent={
          loadingMore ? (
            <View style={styles.loadingMore}>
              <ActivityIndicator size="small" color={COLORS.primary} />
            </View>
          ) : null
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>🛣️</Text>
            <Text style={styles.emptyText}>No incidents reported yet</Text>
            <Text style={styles.emptySubtext}>Be the first to help your community!</Text>
          </View>
        }
      />

      {/* Report FAB */}
      <TouchableOpacity 
        style={styles.fab}
        onPress={() => setShowReportModal(true)}
      >
        <Text style={styles.fabText}>➕</Text>
      </TouchableOpacity>

      {/* Enhanced Report Modal */}
      <EnhancedIncidentReport
        visible={showReportModal}
        onClose={() => setShowReportModal(false)}
        onSuccess={() => loadFeed(1, true)}
      />

      {/* Mini Profile Modal */}
      <MiniProfileModal
        userId={selectedUserId}
        visible={!!selectedUserId}
        onClose={() => setSelectedUserId(null)}
        currentUserId={user?.id}
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 16,
    backgroundColor: COLORS.card,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  chatIconBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: COLORS.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
  },
  chatIcon: {
    fontSize: 22,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  subtitle: {
    fontSize: 14,
    color: COLORS.textDim,
    marginTop: 4,
  },
  listContent: {
    padding: 16,
    paddingBottom: 100, // Extra space for the Map/Feed toggle
  },
  card: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  reporterInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
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
  reporterDetails: {
    marginLeft: 12,
    flex: 1,
  },
  reporterNameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  badgeIcon: {
    fontSize: 16,
  },
  reporterName: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
  },
  timeText: {
    fontSize: 13,
    color: COLORS.textDim,
    marginTop: 2,
  },
  verifiedBadge: {
    backgroundColor: 'rgba(34, 197, 94, 0.2)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  verifiedText: {
    fontSize: 12,
    color: '#22c55e',
    fontWeight: '600',
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  typeBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    marginBottom: 12,
    gap: 8,
  },
  typeIcon: {
    fontSize: 24,
  },
  typeLabel: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  description: {
    fontSize: 15,
    color: COLORS.text,
    lineHeight: 22,
    marginBottom: 12,
  },
  mediaImage: {
    width: '100%',
    height: 200,
    borderRadius: 12,
    marginBottom: 12,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'flex-start',
    gap: 24,
    marginBottom: 8,
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
  },
  statLabel: {
    fontSize: 11,
    color: COLORS.textDim,
    marginTop: 2,
  },
  mapButton: {
    marginTop: 12,
    paddingVertical: 10,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  mapButtonText: {
    fontSize: 14,
    color: COLORS.primary,
    fontWeight: '600',
  },
  loadingMore: {
    paddingVertical: 20,
    alignItems: 'center',
  },
  emptyState: {
    alignItems: 'center',
    paddingTop: 80,
  },
  emptyIcon: {
    fontSize: 64,
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
  fab: {
    position: 'absolute',
    bottom: 90,
    right: 20,
    backgroundColor: COLORS.primary,
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 8,
  },
  fabText: {
    fontSize: 24,
    color: COLORS.background,
  },
});
