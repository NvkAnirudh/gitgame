/**
 * Game Sessions API Service
 */

import api from './api';

export interface GameSession {
  id: string;
  player_id: string;
  started_at: string;
  ended_at?: string;
  duration_seconds?: number;
  lessons_completed: number;
  challenges_completed: number;
  xp_earned: number;
  is_active: boolean;
}

export interface SessionStats {
  total_sessions: number;
  total_playtime_seconds: number;
  average_session_duration_seconds: number;
  total_xp_earned: number;
  total_lessons_completed: number;
  total_challenges_completed: number;
  longest_session_seconds: number;
  current_streak_days: number;
}

export const sessionsService = {
  /**
   * Start a new game session
   */
  async startSession(): Promise<GameSession> {
    const response = await api.post('/sessions/start');
    return response.data;
  },

  /**
   * End active session
   */
  async endSession(sessionId: string): Promise<GameSession> {
    const response = await api.post('/sessions/end', { session_id: sessionId });
    return response.data;
  },

  /**
   * Get current active session
   */
  async getCurrentSession(): Promise<GameSession | null> {
    const response = await api.get('/sessions/current');
    return response.data;
  },

  /**
   * Get session history
   */
  async getSessionHistory(limit: number = 20): Promise<GameSession[]> {
    const response = await api.get(`/sessions/history?limit=${limit}`);
    return response.data;
  },

  /**
   * Get specific session
   */
  async getSession(sessionId: string): Promise<GameSession> {
    const response = await api.get(`/sessions/${sessionId}`);
    return response.data;
  },

  /**
   * Get session statistics
   */
  async getMySessionStats(): Promise<SessionStats> {
    const response = await api.get('/sessions/stats/me');
    return response.data;
  },

  /**
   * Increment lesson count in session
   */
  async incrementLessonCount(sessionId: string): Promise<GameSession> {
    const response = await api.post(`/sessions/${sessionId}/increment-lesson`);
    return response.data;
  },

  /**
   * Increment challenge count in session
   */
  async incrementChallengeCount(sessionId: string, xpEarned: number = 0): Promise<GameSession> {
    const response = await api.post(
      `/sessions/${sessionId}/increment-challenge?xp_earned=${xpEarned}`
    );
    return response.data;
  },
};

export default sessionsService;
