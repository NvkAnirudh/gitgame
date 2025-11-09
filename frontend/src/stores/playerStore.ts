import { create } from 'zustand';
import type { Player, PlayerStats, PlayerProgress } from '../types/api';
import { playersService } from '../services/players';
import { lessonsService } from '../services/lessons';

interface PlayerState {
  player: Player | null;
  stats: PlayerStats | null;
  progress: PlayerProgress[];
  isLoading: boolean;
  error: string | null;

  // Actions
  loadPlayer: () => Promise<void>;
  loadStats: () => Promise<void>;
  loadProgress: () => Promise<void>;
  updateXP: (xp: number) => void;
  clearPlayer: () => void;
}

export const usePlayerStore = create<PlayerState>((set, get) => ({
  player: null,
  stats: null,
  progress: [],
  isLoading: false,
  error: null,

  loadPlayer: async () => {
    set({ isLoading: true, error: null });
    try {
      const player = await playersService.getMyProfile();
      set({ player, isLoading: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to load player';
      set({ error: errorMessage, isLoading: false });
    }
  },

  loadStats: async () => {
    try {
      const stats = await playersService.getMyStats();
      set({ stats });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to load stats';
      set({ error: errorMessage });
    }
  },

  loadProgress: async () => {
    try {
      const progress = await lessonsService.getMyProgress();
      set({ progress });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to load progress';
      set({ error: errorMessage });
    }
  },

  updateXP: (xp: number) => {
    const { player } = get();
    if (player) {
      set({ player: { ...player, total_xp: player.total_xp + xp } });
    }
  },

  clearPlayer: () => set({ player: null, stats: null, progress: [], error: null }),
}));
