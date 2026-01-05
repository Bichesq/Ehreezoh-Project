import { api } from './api';

export interface ChatRoom {
  id: string;
  name: string;
  neighborhood_id: string;
  unread_count: number;
  last_message?: {
    content: string;
    created_at: string;
  };
  member_count: number;
}

export interface ChatMessage {
  id: string;
  room_id: string;
  content: string;
  message_type: string;
  reference_id?: string;
  is_pinned: boolean;
  created_at: string;
  user: {
    id: string;
    name: string;
    profile_photo_url?: string;
    trust_score: number;
  };
  is_own: boolean;
}

export const chatService = {
  // Rooms
  getMyRooms: async (): Promise<ChatRoom[]> => {
    const response = await api.get('/chat/rooms');
    return response.data;
  },

  getRoomDetails: async (roomId: string): Promise<any> => {
    const response = await api.get(`/chat/rooms/${roomId}`);
    return response.data;
  },

  // Messages
  getMessages: async (roomId: string, limit: number = 50, before?: string): Promise<ChatMessage[]> => {
    const params: any = { limit };
    if (before) params.before = before;
    const response = await api.get(`/chat/rooms/${roomId}/messages`, { params });
    return response.data;
  },

  sendMessage: async (roomId: string, content: string, messageType: string = 'text', referenceId?: string): Promise<ChatMessage> => {
    const response = await api.post(`/chat/rooms/${roomId}/messages`, {
      content,
      message_type: messageType,
      reference_id: referenceId
    });
    return response.data;
  },

  // Moderation
  pinMessage: async (roomId: string, messageId: string): Promise<{ success: boolean; is_pinned: boolean }> => {
    const response = await api.post(`/chat/rooms/${roomId}/messages/${messageId}/pin`);
    return response.data;
  },

  deleteMessage: async (roomId: string, messageId: string): Promise<{ success: boolean }> => {
    const response = await api.delete(`/chat/rooms/${roomId}/messages/${messageId}`);
    return response.data;
  }
};
