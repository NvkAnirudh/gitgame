/**
 * Challenges API Service
 */

import api from './api';

export interface Challenge {
  id: string;
  lesson_id: string;
  title: string;
  type: 'crisis' | 'command_mastery' | 'quiz' | 'speed_run' | 'boss';
  difficulty?: number;
  scenario: string;
  success_criteria: Record<string, any>;
  hints?: string[];
  git_state?: Record<string, any>;
  time_limit_seconds?: number;
  max_score: number;
  created_at: string;
}

export interface ChallengeListItem {
  id: string;
  lesson_id: string;
  title: string;
  type: string;
  difficulty?: number;
  max_score: number;
  time_limit_seconds?: number;
}

export interface ChallengeAttempt {
  id: string;
  player_id: string;
  challenge_id: string;
  started_at: string;
  completed_at?: string;
  success: boolean;
  commands_used?: string[];
  score: number;
  time_taken_seconds?: number;
  hints_used: number;
  feedback?: string;
}

export interface LeaderboardEntry {
  player_username: string;
  score: number;
  time_taken_seconds: number;
  completed_at: string;
  rank: number;
}

export interface ChallengeStats {
  challenge_id: string;
  total_attempts: number;
  successful_attempts: number;
  success_rate: number;
  average_score: number;
  average_time_seconds: number;
  fastest_time_seconds?: number;
}

export const challengesService = {
  /**
   * Get list of challenges
   */
  async getChallenges(filters?: { lesson_id?: string; type?: string }): Promise<ChallengeListItem[]> {
    const params = new URLSearchParams();
    if (filters?.lesson_id) params.append('lesson_id', filters.lesson_id);
    if (filters?.type) params.append('type', filters.type);

    const response = await api.get(`/challenges?${params.toString()}`);
    return response.data;
  },

  /**
   * Get challenge details
   */
  async getChallenge(challengeId: string): Promise<Challenge> {
    const response = await api.get(`/challenges/${challengeId}`);
    return response.data;
  },

  /**
   * Start a challenge
   */
  async startChallenge(challengeId: string): Promise<ChallengeAttempt> {
    const response = await api.post('/challenges/start', {
      challenge_id: challengeId,
    });
    return response.data;
  },

  /**
   * Submit challenge solution
   */
  async submitChallenge(
    challengeId: string,
    data: {
      commands_used: string[];
      time_taken_seconds: number;
      hints_used?: number;
      final_state?: Record<string, any>;
    }
  ): Promise<ChallengeAttempt> {
    const response = await api.post(`/challenges/${challengeId}/submit`, data);
    return response.data;
  },

  /**
   * Get player's challenge attempts
   */
  async getMyChallengeAttempts(challengeId: string): Promise<ChallengeAttempt[]> {
    const response = await api.get(`/challenges/${challengeId}/attempts`);
    return response.data;
  },

  /**
   * Get challenge leaderboard
   */
  async getLeaderboard(challengeId: string, limit: number = 10): Promise<LeaderboardEntry[]> {
    const response = await api.get(`/challenges/${challengeId}/leaderboard?limit=${limit}`);
    return response.data;
  },

  /**
   * Get challenge statistics
   */
  async getChallengeStats(challengeId: string): Promise<ChallengeStats> {
    const response = await api.get(`/challenges/${challengeId}/stats`);
    return response.data;
  },
};

export default challengesService;
