import { api } from './api';
import { offlineService } from './offline';

export interface Incident {
  id: string;
  type: string;
  description?: string;
  latitude: number;
  longitude: number;
  created_at: string;
  confirmations: number;
  is_verified?: boolean;
  status?: 'active' | 'resolved' | 'expired';
}

export interface VerificationResponse {
  success: boolean;
  message: string;
  new_status?: string;
}

export const incidentService = {
  reportIncident: async (data: { 
    type: string; 
    description?: string; 
    latitude: number; 
    longitude: number;
    media_url?: string;
  }) => {
    try {
        const response = await api.post('/incidents/', data);
        return response.data;
    } catch (e: any) {
        if (e.message === 'Network Error' || (e.response && e.response.status >= 500)) {
            // Offline queue
            const queued = await offlineService.saveOfflineReport(data);
            if (queued) {
                return { status: 'queued', message: 'Report saved offline. Will sync when online.' };
            }
        }
        throw e;
    }
  },

  getNearbyIncidents: async (latitude: number, longitude: number, radiusKm: number = 5.0) => {
    try {
        const response = await api.get('/incidents/', {
          params: { latitude, longitude, radius_km: radiusKm }
        });
        const incidents = response.data as Incident[];
        
        // Cache successful response
        await offlineService.cacheIncidents(incidents);
        
        return incidents;
    } catch (e: any) {
        console.log("Fetching incidents failed, trying cache...");
        // Return cached if API fails (offline or server error)
        if (e.message === 'Network Error' || !e.response || e.response.status >= 500) {
            const cached = await offlineService.getCachedIncidents();
            if (cached.length > 0) return cached;
        }
        throw e;
    }
  },

  /**
   * Verify an incident with 'still_there' or 'all_clear'.
   * Requires trust_score >= 25.
   */
  verifyIncident: async (incidentId: string, verificationType: 'still_there' | 'all_clear'): Promise<VerificationResponse> => {
    const response = await api.post(`/community/incidents/${incidentId}/verify`, {
      verification_type: verificationType
    });
    return response.data;
  },

  syncOfflineReports: async () => {
    const reports = await offlineService.getOfflineReports();
    if (reports.length === 0) return;

    console.log(`[Sync] Processing ${reports.length} offline reports...`);
    
    // Process sequentially to maintain order
    for (const report of reports) {
      try {
        const { id, data } = report;
        
        // TODO: Implement actual photo upload here when backend supports it
        // If data.photoUri exists, upload it and get media_url
        // const media_url = await uploadPhoto(data.photoUri);
        // const payload = { ...data, media_url };
        
        console.log(`[Sync] Sending report ${id}...`);
        
        // We use api directly here to avoid re-triggering offline save loop
        // Also strip photoUri as backend doesn't expect it
        const { photoUri, ...payload } = data;
        
        await api.post('/incidents/', payload);
        
        // Remove from queue on success
        await offlineService.removeReport(id);
        console.log(`[Sync] Report ${id} synced successfully.`);
        
      } catch (e) {
        console.error(`[Sync] Failed to sync report ${report.id}`, e);
        // Keep in queue to retry later
      }
    }
  }
};
