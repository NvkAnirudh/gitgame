import api from './api';
import type { Player, PlayerStats } from '../types/api';

export const playersService = {
  /**
   * Get current player profile
   */
  async getMyProfile(): Promise<Player> {
    const response = await api.get<Player>('/players/me');
    return response.data;
  },

  /**
   * Get current player statistics
   */
  async getMyStats(): Promise<PlayerStats> {
    const response = await api.get<PlayerStats>('/players/me/stats');
    return response.data;
  },
};
