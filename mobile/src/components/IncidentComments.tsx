import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, FlatList, ActivityIndicator, Alert } from 'react-native';
import { socialService, Comment } from '../services/social';
import { COLORS } from '../constants/colors';

interface IncidentCommentsProps {
  incidentId: string;
  onCommentAdded?: () => void;
}

export default function IncidentComments({ incidentId, onCommentAdded }: IncidentCommentsProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadComments();
  }, [incidentId]);

  const loadComments = async () => {
    try {
      const data = await socialService.getComments(incidentId);
      setComments(data);
    } catch (error) {
      console.error('Failed to load comments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!newComment.trim()) return;
    if (newComment.length > 280) {
      Alert.alert('Too long', 'Comments must be 280 characters or less');
      return;
    }

    setSubmitting(true);
    try {
      const comment = await socialService.addComment(incidentId, newComment.trim());
      setComments([comment, ...comments]);
      setNewComment('');
      onCommentAdded?.();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to add comment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpvote = async (commentId: string) => {
    try {
      const result = await socialService.upvoteComment(commentId);
      setComments(comments.map(c => 
        c.id === commentId 
          ? { ...c, upvotes: result.upvotes, has_upvoted: result.action === 'added' }
          : c
      ));
    } catch (error) {
      console.error('Failed to upvote:', error);
    }
  };

  const getTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMins = Math.floor((now.getTime() - date.getTime()) / 60000);
    if (diffMins < 1) return 'now';
    if (diffMins < 60) return `${diffMins}m`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h`;
    return `${Math.floor(diffHours / 24)}d`;
  };

  const renderComment = ({ item }: { item: Comment }) => (
    <View style={styles.commentCard}>
      <View style={styles.commentHeader}>
        <Text style={styles.commentAuthor}>{item.user.name}</Text>
        <Text style={styles.commentTime}>{getTimeAgo(item.created_at)}</Text>
      </View>
      <Text style={styles.commentContent}>{item.content}</Text>
      <TouchableOpacity 
        style={[styles.upvoteBtn, item.has_upvoted && styles.upvotedBtn]}
        onPress={() => handleUpvote(item.id)}
      >
        <Text style={[styles.upvoteText, item.has_upvoted && styles.upvotedText]}>
          👍 {item.upvotes || 0}
        </Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>💬 Comments</Text>
      
      {/* Input */}
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          placeholder="Add update..."
          placeholderTextColor={COLORS.textDim}
          value={newComment}
          onChangeText={setNewComment}
          maxLength={280}
          multiline
        />
        <TouchableOpacity 
          style={[styles.sendBtn, !newComment.trim() && styles.sendBtnDisabled]}
          onPress={handleSubmit}
          disabled={!newComment.trim() || submitting}
        >
          {submitting ? (
            <ActivityIndicator size="small" color="#FFF" />
          ) : (
            <Text style={styles.sendBtnText}>Post</Text>
          )}
        </TouchableOpacity>
      </View>
      <Text style={styles.charCount}>{newComment.length}/280</Text>

      {/* Comments List */}
      {loading ? (
        <ActivityIndicator size="small" color={COLORS.primary} style={{ marginTop: 20 }} />
      ) : comments.length === 0 ? (
        <Text style={styles.noComments}>No comments yet. Be first!</Text>
      ) : (
        <FlatList
          data={comments}
          renderItem={renderComment}
          keyExtractor={(item) => item.id}
          scrollEnabled={false}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 12,
  },
  inputRow: {
    flexDirection: 'row',
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: COLORS.background,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: COLORS.text,
    fontSize: 14,
    maxHeight: 80,
  },
  sendBtn: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 16,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendBtnDisabled: {
    opacity: 0.5,
  },
  sendBtnText: {
    color: COLORS.background,
    fontWeight: 'bold',
    fontSize: 14,
  },
  charCount: {
    fontSize: 11,
    color: COLORS.textDim,
    textAlign: 'right',
    marginTop: 4,
  },
  noComments: {
    fontSize: 14,
    color: COLORS.textDim,
    textAlign: 'center',
    marginTop: 20,
  },
  commentCard: {
    backgroundColor: COLORS.background,
    padding: 12,
    borderRadius: 10,
    marginTop: 10,
  },
  commentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  commentAuthor: {
    fontSize: 13,
    fontWeight: '600',
    color: COLORS.text,
  },
  commentTime: {
    fontSize: 12,
    color: COLORS.textDim,
  },
  commentContent: {
    fontSize: 14,
    color: COLORS.text,
    lineHeight: 20,
  },
  upvoteBtn: {
    marginTop: 8,
    alignSelf: 'flex-start',
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  upvotedBtn: {
    backgroundColor: 'rgba(2, 221, 237, 0.2)',
  },
  upvoteText: {
    fontSize: 13,
    color: COLORS.textDim,
  },
  upvotedText: {
    color: COLORS.primary,
  },
});
