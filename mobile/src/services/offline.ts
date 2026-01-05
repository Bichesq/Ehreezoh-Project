import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { DeviceEventEmitter } from 'react-native';
import { Incident } from './incident';

const KEYS = {
  OFFLINE_REPORTS: 'offline_reports_queue',
  CACHED_INCIDENTS: 'cached_incidents',
};

export interface OfflineReport {
  id: string;
  data: {
    type: string;
    description?: string;
    latitude: number;
    longitude: number;
    photoUri?: string; // Future proofing
  };
  timestamp: number;
}

export const offlineService = {
  // --- Network Status ---
  isOnline: async () => {
    const state = await NetInfo.fetch();
    return state.isConnected && state.isInternetReachable;
  },

  // --- Incident Caching ---
  cacheIncidents: async (incidents: Incident[]) => {
    try {
      await AsyncStorage.setItem(KEYS.CACHED_INCIDENTS, JSON.stringify(incidents));
    } catch (e) {
      console.error('[Offline] Failed to cache incidents', e);
    }
  },

  getCachedIncidents: async (): Promise<Incident[]> => {
    try {
      const json = await AsyncStorage.getItem(KEYS.CACHED_INCIDENTS);
      return json ? JSON.parse(json) : [];
    } catch (e) {
      console.error('[Offline] Failed to load cached incidents', e);
      return [];
    }
  },

  // --- Offline Reporting ---
  saveOfflineReport: async (data: OfflineReport['data']) => {
    try {
      const newReport: OfflineReport = {
        id: Date.now().toString(),
        data,
        timestamp: Date.now(),
      };

      const existingJson = await AsyncStorage.getItem(KEYS.OFFLINE_REPORTS);
      const existing: OfflineReport[] = existingJson ? JSON.parse(existingJson) : [];
      
      const updated = [...existing, newReport];
      await AsyncStorage.setItem(KEYS.OFFLINE_REPORTS, JSON.stringify(updated));
      
      console.log('[Offline] Report queued:', newReport.id);
      DeviceEventEmitter.emit('offline_report_queued', { count: updated.length });
      return true;
    } catch (e) {
      console.error('[Offline] Failed to queue report', e);
      return false;
    }
  },

  getOfflineReports: async (): Promise<OfflineReport[]> => {
    try {
      const json = await AsyncStorage.getItem(KEYS.OFFLINE_REPORTS);
      return json ? JSON.parse(json) : [];
    } catch (e) {
      return [];
    }
  },

  clearOfflineReports: async () => {
    await AsyncStorage.removeItem(KEYS.OFFLINE_REPORTS);
    DeviceEventEmitter.emit('offline_reports_synced');
  },
    
  removeReport: async (id: string) => {
    try {
        const reports = await offlineService.getOfflineReports();
        const updated = reports.filter(r => r.id !== id);
        await AsyncStorage.setItem(KEYS.OFFLINE_REPORTS, JSON.stringify(updated));
    } catch (e) {
        console.error("Failed to remove report", e);
    }
  }
};
