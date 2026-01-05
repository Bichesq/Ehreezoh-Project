import { api } from './api';

export interface Comment {
  id: string;
  incident_id: string;
  content: string;
  upvotes: number;
  created_at: string;
  user: {
    id: string;
    name: string;
    profile_photo_url?: string;
    trust_score: number;
  };
  has_upvoted: boolean;
}

export interface ThanksResponse {
  success: boolean;
  message: string;
  total_thanks: number;
}

export interface ThanksInfo {
  incident_id: string;
  total_thanks: number;
  has_thanked: boolean;
}

export const socialService = {
  // Thanks
  sayThanks: async (incidentId: string): Promise<ThanksResponse> => {
    const response = await api.post('/social/thanks', { incident_id: incidentId });
    return response.data;
  },

  getThanksInfo: async (incidentId: string): Promise<ThanksInfo> => {
    const response = await api.get(`/social/thanks/${incidentId}`);
    return response.data;
  },

  // Comments
  getComments: async (incidentId: string): Promise<Comment[]> => {
    const response = await api.get(`/social/incidents/${incidentId}/comments`);
    return response.data;
  },

  addComment: async (incidentId: string, content: string): Promise<Comment> => {
    const response = await api.post(`/social/incidents/${incidentId}/comments`, { content });
    return response.data;
  },

  upvoteComment: async (commentId: string): Promise<{ success: boolean; action: string; upvotes: number }> => {
    const response = await api.post(`/social/comments/${commentId}/upvote`);
    return response.data;
  },

  // Impact
  getMyImpact: async (): Promise<{
    thanks_received: number;
    comments_made: number;
    upvotes_received: number;
    total_people_helped: number;
  }> => {
    const response = await api.get('/social/my-impact');
    return response.data;
  },

  // Follow
  followUser: async (userId: string): Promise<{ success: boolean; message: string; follower_count: number }> => {
    const response = await api.post(`/social/follow/${userId}`);
    return response.data;
  },

  unfollowUser: async (userId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/social/follow/${userId}`);
    return response.data;
  },

  getFollowStatus: async (userId: string): Promise<{
    user_id: string;
    is_following: boolean;
    follower_count: number;
    following_count: number;
  }> => {
    const response = await api.get(`/social/follow/${userId}/status`);
    return response.data;
  },

  getFollowing: async (): Promise<{ count: number; following: Array<{ id: string; name: string; profile_photo_url?: string; trust_score: number }> }> => {
    const response = await api.get('/social/following');
    return response.data;
  },

  getFollowers: async (): Promise<{ count: number; followers: Array<{ id: string; name: string; profile_photo_url?: string; trust_score: number }> }> => {
    const response = await api.get('/social/followers');
    return response.data;
  }
};
