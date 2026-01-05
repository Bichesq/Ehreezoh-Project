import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Image,
  Animated,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { chatService, ChatMessage } from '../../services/chat';
import { socketService } from '../../services/socket';
import { useAuth } from '../../context/AuthContext';
import { COLORS } from '../../constants/colors';

export default function ChatScreen() {
  const router = useRouter();
  const { roomId } = useLocalSearchParams<{ roomId: string }>();
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const [roomName, setRoomName] = useState('Chat');
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  
  const flatListRef = useRef<FlatList>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (roomId) {
      loadRoom();
      loadMessages();
      
      // Real-time setup
      socketService.joinChat(roomId!);
      
      const unsubscribe = socketService.addListener((event) => {
        if (event.type === 'new_message' && event.data.room_id === roomId) {
           // Append new message (if not already there - though backend excludes sender)
           setMessages(prev => {
               if (prev.find(m => m.id === event.data.id)) return prev;
               return [...prev, event.data];
           });
           setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100);
        }
        
        if (event.type === 'typing' && event.data.room_id === roomId) {
            const { user_name, is_typing } = event.data;
            setTypingUsers(prev => {
                if (is_typing) {
                    if (!prev.includes(user_name)) return [...prev, user_name];
                    return prev;
                } else {
                    return prev.filter(u => u !== user_name);
                }
            });
        }
      });
      
      return () => {
        unsubscribe();
        socketService.leaveChat(roomId!);
      };
    }
  }, [roomId]);

  const loadRoom = async () => {
    try {
      const room = await chatService.getRoomDetails(roomId!);
      setRoomName(room.name);
    } catch (error) {
      console.error('Failed to load room:', error);
    }
  };

  const loadMessages = async () => {
    try {
      const data = await chatService.getMessages(roomId!);
      // Reverse because backend returns desc, but we want chrono? 
      // Backend api/chat.py says: "reversed(messages)" so it is chronological. ok.
      setMessages(data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTyping = (text: string) => {
    setNewMessage(text);
    
    if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
    } else {
        socketService.sendTyping(roomId!, true);
    }
    
    typingTimeoutRef.current = setTimeout(() => {
        socketService.sendTyping(roomId!, false);
        typingTimeoutRef.current = null;
    }, 2000);
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || sending) return;

    // Clear typing status immediately
    if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
        socketService.sendTyping(roomId!, false);
        typingTimeoutRef.current = null;
    }

    setSending(true);
    try {
      const msg = await chatService.sendMessage(roomId!, newMessage.trim());
      setMessages(prev => [...prev, msg]);
      setNewMessage('');
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } catch (error) {
      console.error('Failed to send:', error);
    } finally {
      setSending(false);
    }
  };

  const getTimeStr = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderMessage = ({ item }: { item: ChatMessage }) => (
    <View style={[styles.messageRow, item.is_own && styles.ownMessageRow]}>
      {!item.is_own && (
        <View style={styles.avatar}>
          {item.user.profile_photo_url ? (
            <Image source={{ uri: item.user.profile_photo_url }} style={styles.avatarImg} />
          ) : (
            <Text style={styles.avatarText}>{item.user.name?.charAt(0) || '?'}</Text>
          )}
        </View>
      )}
      <View style={[styles.messageBubble, item.is_own && styles.ownBubble]}>
        {!item.is_own && (
          <Text style={styles.senderName}>{item.user.name}</Text>
        )}
        <Text style={[styles.messageText, item.is_own && styles.ownMessageText]}>
          {item.content}
        </Text>
        <Text style={[styles.timeText, item.is_own && styles.ownTimeText]}>
          {getTimeStr(item.created_at)}
        </Text>
        {item.is_pinned && (
          <Text style={styles.pinnedBadge}>📌 Pinned</Text>
        )}
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={0}
    >
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backText}>←</Text>
        </TouchableOpacity>
        <View style={styles.headerInfo}>
          <Text style={styles.roomName}>{roomName}</Text>
          <Text style={styles.roomSubtitle}>Neighborhood Chat</Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.messageList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: false })}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>💬</Text>
            <Text style={styles.emptyText}>No messages yet</Text>
            <Text style={styles.emptySubtext}>Be the first to say hello!</Text>
          </View>
        }
        ListFooterComponent={
            typingUsers.length > 0 ? (
                <View style={styles.typingContainer}>
                    <Text style={styles.typingText}>
                        {typingUsers.join(', ')} {typingUsers.length > 1 ? 'are' : 'is'} typing...
                    </Text>
                </View>
            ) : null
        }
      />

      {/* Input */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Type a message..."
          placeholderTextColor={COLORS.textDim}
          value={newMessage}
          onChangeText={handleTyping}
          multiline
          maxLength={1000}
        />
        <TouchableOpacity 
          style={[styles.sendBtn, !newMessage.trim() && styles.sendBtnDisabled]}
          onPress={sendMessage}
          disabled={!newMessage.trim() || sending}
        >
          {sending ? (
            <ActivityIndicator size="small" color={COLORS.background} />
          ) : (
            <Text style={styles.sendBtnText}>➤</Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 50,
    paddingHorizontal: 16,
    paddingBottom: 12,
    backgroundColor: COLORS.card,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  backBtn: {
    padding: 8,
  },
  backText: {
    fontSize: 24,
    color: COLORS.text,
  },
  headerInfo: {
    flex: 1,
    marginLeft: 12,
  },
  roomName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  roomSubtitle: {
    fontSize: 12,
    color: COLORS.textDim,
  },
  messageList: {
    padding: 16,
    paddingBottom: 8,
  },
  messageRow: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'flex-end',
  },
  ownMessageRow: {
    justifyContent: 'flex-end',
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: COLORS.border,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  avatarImg: {
    width: 32,
    height: 32,
    borderRadius: 16,
  },
  avatarText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: COLORS.textDim,
  },
  messageBubble: {
    maxWidth: '75%',
    backgroundColor: COLORS.card,
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    padding: 12,
    paddingBottom: 8,
  },
  ownBubble: {
    backgroundColor: COLORS.primary,
    borderBottomLeftRadius: 18,
    borderBottomRightRadius: 4,
  },
  senderName: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.primary,
    marginBottom: 4,
  },
  messageText: {
    fontSize: 15,
    color: COLORS.text,
    lineHeight: 20,
  },
  ownMessageText: {
    color: COLORS.background,
  },
  timeText: {
    fontSize: 10,
    color: COLORS.textDim,
    marginTop: 4,
    alignSelf: 'flex-end',
  },
  ownTimeText: {
    color: 'rgba(255,255,255,0.7)',
  },
  pinnedBadge: {
    fontSize: 10,
    color: COLORS.primary,
    marginTop: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 12,
    backgroundColor: COLORS.card,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  input: {
    flex: 1,
    backgroundColor: COLORS.background,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    color: COLORS.text,
    fontSize: 15,
    maxHeight: 100,
  },
  sendBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  sendBtnDisabled: {
    opacity: 0.5,
  },
  sendBtnText: {
    fontSize: 20,
    color: COLORS.background,
  },
  emptyState: {
    alignItems: 'center',
    paddingTop: 60,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
  },
  emptySubtext: {
    fontSize: 14,
    color: COLORS.textDim,
    marginTop: 4,
  },
  typingContainer: {
    padding: 8,
    marginLeft: 40, 
    marginBottom: 8,
  },
  typingText: {
    fontSize: 12,
    color: COLORS.textDim,
    fontStyle: 'italic',
  }
});
