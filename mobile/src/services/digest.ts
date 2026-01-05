import { api } from './api';

export interface WeeklyDigest {
  period: {
    start: string;
    end: string;
  };
  my_stats: {
    reports_made: number;
    thanks_received: number;
    new_followers: number;
  };
  community_stats: {
    total_incidents: number;
    total_thanks: number;
    followed_reports: number;
  };
  top_reporter?: {
    id: string;
    name: string;
    report_count: number;
  };
  highlights: string[];
  message: string;
}

export const digestService = {
  getWeeklyDigest: async (): Promise<WeeklyDigest> => {
    const response = await api.get('/digest/weekly');
    return response.data;
  }
};
