import api from './api';

export const voteService = {
  /**
   * Verify an incident (Vote "Still There" or "All Clear")
   * @param incidentId 
   * @param type 'still_there' | 'all_clear'
   */
  verifyIncident: async (incidentId: string, type: 'still_there' | 'all_clear') => {
    try {
      const response = await api.post(`/incidents/${incidentId}/verify`, {
        verification_type: type
      });
      return response.data;
    } catch (error) {
      console.error('Vote failed:', error);
      throw error;
    }
  }
};
