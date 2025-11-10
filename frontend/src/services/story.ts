/**
 * Story & Narrative API Service
 */

import api from './api';

export interface Character {
  id: string;
  name: string;
  title?: string;
  avatar_url?: string;
  bio?: string;
  personality?: Record<string, any>;
  specialization?: string;
}

export interface StoryArc {
  id: string;
  name: string;
  description?: string;
  level: 'introduction' | 'intermediate' | 'advanced';
  mentor_id?: string;
  mentor?: Character;
  order_index: number;
  total_lessons: number;
  status?: 'locked' | 'unlocked' | 'in_progress' | 'completed';
}

export interface PlayerStoryProgress {
  id: string;
  player_id: string;
  story_arc_id: string;
  story_arc?: StoryArc;
  status: 'locked' | 'unlocked' | 'in_progress' | 'completed';
  unlocked_at?: string;
  started_at?: string;
  completed_at?: string;
  lessons_completed: number;
}

export interface MentorTip {
  character: Character;
  tip: string;
  context: string;
}

export interface StoryContext {
  current_arc?: StoryArc;
  current_mentor?: Character;
  arcs_completed: number;
  total_arcs: number;
  lessons_in_current_arc: number;
  lessons_completed_in_arc: number;
  next_milestone?: string;
}

export const storyService = {
  /**
   * Get all characters/mentors
   */
  async getCharacters(): Promise<Character[]> {
    const response = await api.get('/story/characters');
    return response.data;
  },

  /**
   * Get specific character
   */
  async getCharacter(characterId: string): Promise<Character> {
    const response = await api.get(`/story/characters/${characterId}`);
    return response.data;
  },

  /**
   * Get all story arcs with player progress
   */
  async getStoryArcs(): Promise<StoryArc[]> {
    const response = await api.get('/story/arcs');
    return response.data;
  },

  /**
   * Get specific story arc
   */
  async getStoryArc(arcId: string): Promise<StoryArc> {
    const response = await api.get(`/story/arcs/${arcId}`);
    return response.data;
  },

  /**
   * Get player's story progression
   */
  async getMyProgress(): Promise<PlayerStoryProgress[]> {
    const response = await api.get('/story/progress');
    return response.data;
  },

  /**
   * Get current story context
   */
  async getStoryContext(): Promise<StoryContext> {
    const response = await api.get('/story/context');
    return response.data;
  },

  /**
   * Get mentor tip for a lesson
   */
  async getMentorTip(lessonId: string): Promise<MentorTip> {
    const response = await api.get(`/story/mentor/tip/${lessonId}`);
    return response.data;
  },
};

export default storyService;
