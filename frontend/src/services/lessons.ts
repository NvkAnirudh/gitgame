import api from './api';
import type {
  Lesson,
  LessonListItem,
  PlayerProgress,
  StartLessonRequest,
  CompleteLessonRequest,
} from '../types/api';

export const lessonsService = {
  /**
   * Get list of all lessons
   */
  async getLessons(level?: string): Promise<LessonListItem[]> {
    const params = level ? { level } : {};
    const response = await api.get<LessonListItem[]>('/lessons/', { params });
    return response.data;
  },

  /**
   * Get full lesson content by ID
   */
  async getLesson(lessonId: string): Promise<Lesson> {
    const response = await api.get<Lesson>(`/lessons/${lessonId}`);
    return response.data;
  },

  /**
   * Start a lesson
   */
  async startLesson(lessonId: string): Promise<PlayerProgress> {
    const request: StartLessonRequest = { lesson_id: lessonId };
    const response = await api.post<PlayerProgress>('/lessons/start', request);
    return response.data;
  },

  /**
   * Complete a lesson
   */
  async completeLesson(
    lessonId: string,
    timeSpentSeconds: number,
    score?: number
  ): Promise<PlayerProgress> {
    const request: CompleteLessonRequest = {
      lesson_id: lessonId,
      time_spent_seconds: timeSpentSeconds,
      score,
    };
    const response = await api.post<PlayerProgress>('/lessons/complete', request);
    return response.data;
  },

  /**
   * Get my progress for all lessons
   */
  async getMyProgress(): Promise<PlayerProgress[]> {
    const response = await api.get<PlayerProgress[]>('/lessons/progress/me');
    return response.data;
  },

  /**
   * Get progress for specific lesson
   */
  async getLessonProgress(lessonId: string): Promise<PlayerProgress> {
    const response = await api.get<PlayerProgress>(`/lessons/progress/${lessonId}`);
    return response.data;
  },
};
