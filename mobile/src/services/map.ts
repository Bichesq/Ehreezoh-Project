import { api } from './api';
import { Coordinates } from './location';

export interface PlaceResult {
    id: string;
    name: string;
    description: string;
    latitude: number;
    longitude: number;
}

export const mapService = {
    async searchPlaces(query: string, userLocation?: Coordinates): Promise<PlaceResult[]> {
        if (!query || query.length < 2) return [];
        
        try {
            const params: any = { query };
            if (userLocation) {
                params.latitude = userLocation.latitude;
                params.longitude = userLocation.longitude;
            }
            
            const response = await api.get<PlaceResult[]>('/maps/search', { params });
            return response.data;
        } catch (error) {
            console.error('Search failed:', error);
            return [];
        }
    }
};
