import { api } from './api';
import { User } from './auth';

export interface Badge {
    name: string;
    description: string;
    icon: string;
    is_earned: boolean;
    earned_at?: string;
    requirement_value?: number;
    requirement_type?: string;
}

export interface GamificationStats {
    points: number;
    reputation_score: number;
    trust_score: number;
    trust_level: string;
    trust_icon: string;
    next_level_score: number | null;
    total_reports: number;
    total_people_helped: number;
    current_streak: number;
    longest_streak: number;
    badges: Badge[];
}

export const gamificationService = {
    getLeaderboard: async (): Promise<User[]> => {
        const response = await api.get('/gamification/leaderboard');
        return response.data;
    },

    getMyStats: async (): Promise<GamificationStats> => {
        const response = await api.get('/gamification/me');
        return response.data;
    },

    seed: async () => {
        return api.post('/gamification/seed');
    }
};
