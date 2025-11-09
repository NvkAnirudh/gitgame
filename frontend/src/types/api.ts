// API Type Definitions for Git Quest

// ============= Auth Types =============
export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  display_name?: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ============= Player Types =============
export interface Player {
  id: string;
  user_id: string;
  username: string;
  display_name?: string;
  avatar_url?: string;
  created_at: string;
  current_level: string;
  total_xp: number;
}

export interface PlayerStats {
  player_id: string;
  username: string;
  total_xp: number;
  current_level: string;
  lessons_completed: number;
  lessons_in_progress: number;
  challenges_completed: number;
  achievements_unlocked: number;
  total_learning_time_seconds: number;
}

// ============= Lesson Types =============
export interface LessonListItem {
  id: string;
  title: string;
  level: 'introduction' | 'intermediate' | 'advanced';
  order_index: number;
  total_sections: number;
  git_commands?: string[];
}

export interface LessonSection {
  type: 'dialogue' | 'explanation' | 'code' | 'tip';
  speaker?: string;
  content: string;
}

export interface Lesson {
  id: string;
  title: string;
  level: 'introduction' | 'intermediate' | 'advanced';
  order_index: number;
  story_hook?: string;
  content: LessonSection[];
  learning_objectives?: string[];
  practice_prompt?: string;
  git_commands?: string[];
  word_count: number;
  total_sections: number;
}

// ============= Progress Types =============
export interface PlayerProgress {
  id: string;
  player_id: string;
  lesson_id: string;
  status: 'not_started' | 'in_progress' | 'completed';
  started_at?: string;
  completed_at?: string;
  time_spent_seconds: number;
  score?: number;
  attempts: number;
}

export interface StartLessonRequest {
  lesson_id: string;
}

export interface CompleteLessonRequest {
  lesson_id: string;
  time_spent_seconds: number;
  score?: number;
}

// ============= Challenge Types =============
export interface Challenge {
  id: string;
  lesson_id: string;
  title: string;
  type: 'crisis' | 'command_mastery' | 'quiz' | 'speed_run' | 'boss';
  difficulty: number;
  scenario: string;
  success_criteria: Record<string, any>;
  hints?: string[];
  time_limit_seconds?: number;
  max_score: number;
}

// ============= Achievement Types =============
export interface Achievement {
  id: string;
  name: string;
  description: string;
  badge_icon?: string;
  category?: string;
  unlock_criteria: Record<string, any>;
  points: number;
}

// ============= API Response Types =============
export interface ApiError {
  detail: string;
  error?: string;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
}
