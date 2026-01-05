import { api } from './api';
import { Coordinates } from './location';

export interface SafetyPrediction {
    time_label: string;
    timestamp: string;
    safety_score: number;
    risk_level: string;
    historical_incident_count: number;
}

export interface BestTimeResponse {
    predictions: SafetyPrediction[];
    best_time: SafetyPrediction;
}

export const analyticsService = {
    /**
     * Get safety predictions for a route at future times.
     */
    getBestTimeToLeave: async (routePolyline: string): Promise<BestTimeResponse> => {
        const response = await api.get('/analytics/best-time', {
            params: { route_polyline: routePolyline }
        });
        return response.data;
    },

    /**
     * Seeds test data (Dev only)
     */
    seedTestData: async (lat: number, lon: number) => {
        return api.post('/analytics/seed-test-data', null, {
            params: { lat, lon }
        });
    }
};
