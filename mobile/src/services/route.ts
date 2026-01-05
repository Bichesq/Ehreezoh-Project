import { api } from './api';

export interface RouteIncident {
    id: string;
    type: string;
    severity: string;
    description?: string;
    location: [number, number];
}

export interface ScoredRoute {
    id: string;
    geometry_encoded: string;
    distance_km: number;
    duration_minutes: number;
    score: number;
    rank: number;
    label: string;
    incidents: RouteIncident[];
    warnings: string[];
}

export interface RouteAnalysisResponse {
    routes: ScoredRoute[];
    recommendation?: string;
}

export const routeService = {
    analyzeRoutes: async (
        origin: { latitude: number; longitude: number }, 
        destination: { latitude: number; longitude: number },
        rideType: 'moto' | 'economy_car' | 'comfort_car' = 'moto'
    ): Promise<RouteAnalysisResponse> => {
        try {
            const response = await api.post('/routes/analyze', {
                origin: [origin.longitude, origin.latitude],
                destination: [destination.longitude, destination.latitude],
                ride_type: rideType,
                preferences: {
                    prioritize: 'balanced'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Route analysis failed:', error);
            throw error;
        }
    }
};
