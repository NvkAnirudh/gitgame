import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error, clearError } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      // Error is already set in the store
      console.error('Login failed:', err);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center grid-pattern p-4">
      <div className="w-full max-w-md">
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold heading-neon text-glow mb-2 animate-pulse-neon">
            GIT QUEST
          </h1>
          <p className="text-text-secondary">
            master the git timeline
          </p>
        </div>

        {/* Login Card */}
        <div className="card">
          <h2 className="text-2xl font-bold heading-purple mb-6">
            {'>'} login
          </h2>

          {error && (
            <div className="mb-4 p-3 bg-neon-red/10 border border-neon-red/50 rounded text-neon-red text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-text-secondary text-sm mb-2">
                username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="input"
                placeholder="enter username..."
                required
                autoFocus
              />
            </div>

            <div>
              <label className="block text-text-secondary text-sm mb-2">
                password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="enter password..."
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? (
                <span className="loading-dots">authenticating</span>
              ) : (
                'login'
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-text-secondary text-sm">
            <span>new player? </span>
            <Link
              to="/register"
              className="text-neon-cyan hover:text-glow transition-all"
            >
              create account
            </Link>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-text-muted text-xs">
          <p>// adventure awaits in the git timeline</p>
        </div>
      </div>
    </div>
  );
}
