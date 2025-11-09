import api from './api';
import type { User, UserCreate, Token } from '../types/api';

export const authService = {
  /**
   * Register a new user
   */
  async register(userData: UserCreate): Promise<User> {
    const response = await api.post<User>('/auth/register', userData);
    return response.data;
  },

  /**
   * Login with username and password
   * Uses OAuth2 password flow (form data)
   */
  async login(username: string, password: string): Promise<Token> {
    // OAuth2 requires form data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post<Token>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const { access_token, refresh_token } = response.data;

    // Store tokens
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    return response.data;
  },

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } finally {
      // Clear tokens regardless of API response
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Get access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  },
};
