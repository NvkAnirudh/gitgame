import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';
import type { UserCreate } from '../types/api';

export default function Register() {
  const [formData, setFormData] = useState<UserCreate>({
    email: '',
    username: '',
    password: '',
    display_name: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (formData.password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      await authService.register(formData);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Registration failed';
      setError(errorMessage);
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center grid-pattern p-4">
        <div className="w-full max-w-md">
          <div className="card text-center">
            <div className="text-6xl mb-4">✓</div>
            <h2 className="text-2xl font-bold heading-neon mb-2">
              registration complete
            </h2>
            <p className="text-text-secondary mb-4">
              redirecting to login<span className="loading-dots"></span>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center grid-pattern p-4">
      <div className="w-full max-w-md">
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold heading-neon text-glow mb-2 animate-pulse-neon">
            GIT QUEST
          </h1>
          <p className="text-text-secondary">
            begin your journey
          </p>
        </div>

        {/* Register Card */}
        <div className="card">
          <h2 className="text-2xl font-bold heading-purple mb-6">
            {'>'} register
          </h2>

          {error && (
            <div className="mb-4 p-3 bg-neon-red/10 border border-neon-red/50 rounded text-neon-red text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-text-secondary text-sm mb-2">
                email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="input"
                placeholder="your@email.com"
                required
                autoFocus
              />
            </div>

            <div>
              <label className="block text-text-secondary text-sm mb-2">
                username
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="input"
                placeholder="choose username..."
                required
                minLength={3}
                maxLength={50}
              />
              <p className="text-text-muted text-xs mt-1">
                3-50 characters, alphanumeric
              </p>
            </div>

            <div>
              <label className="block text-text-secondary text-sm mb-2">
                display name (optional)
              </label>
              <input
                type="text"
                name="display_name"
                value={formData.display_name}
                onChange={handleChange}
                className="input"
                placeholder="how others see you..."
                maxLength={100}
              />
            </div>

            <div>
              <label className="block text-text-secondary text-sm mb-2">
                password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="input"
                placeholder="create password..."
                required
                minLength={8}
              />
              <p className="text-text-muted text-xs mt-1">
                min 8 chars, 1 uppercase, 1 lowercase, 1 digit
              </p>
            </div>

            <div>
              <label className="block text-text-secondary text-sm mb-2">
                confirm password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input"
                placeholder="confirm password..."
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? (
                <span className="loading-dots">creating account</span>
              ) : (
                'create account'
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-text-secondary text-sm">
            <span>already have an account? </span>
            <Link
              to="/login"
              className="text-neon-cyan hover:text-glow transition-all"
            >
              login
            </Link>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-text-muted text-xs">
          <p>// your git adventure starts here</p>
        </div>
      </div>
    </div>
  );
}
