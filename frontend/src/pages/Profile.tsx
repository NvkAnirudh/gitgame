import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { usePlayerStore } from '../stores/playerStore';

export default function Profile() {
  const { player, stats, loadPlayer, loadStats } = usePlayerStore();

  useEffect(() => {
    loadPlayer();
    loadStats();
  }, []);

  if (!player || !stats) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-neon-cyan text-2xl">
          <span className="loading-dots">loading</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen grid-pattern p-8">
      <div className="max-w-4xl mx-auto">
        <Link to="/dashboard" className="btn btn-ghost mb-6 inline-block">
          ← back to dashboard
        </Link>

        <div className="card mb-6">
          <h1 className="text-4xl font-bold heading-neon mb-2">
            {player.display_name || player.username}
          </h1>
          <p className="text-text-secondary">@{player.username}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-xl font-bold heading-purple mb-4">
              {'>'} stats
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-text-secondary">Total XP</span>
                <span className="text-neon-green font-bold">{stats.total_xp}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Current Level</span>
                <span className="text-neon-cyan">{stats.current_level}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Lessons Completed</span>
                <span className="text-text-primary">{stats.lessons_completed}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">In Progress</span>
                <span className="text-text-primary">{stats.lessons_in_progress}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Achievements</span>
                <span className="text-text-primary">{stats.achievements_unlocked}</span>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-bold heading-purple mb-4">
              {'>'} info
            </h2>
            <div className="space-y-3">
              <div>
                <p className="text-text-muted text-sm">Member Since</p>
                <p className="text-text-primary">
                  {new Date(player.created_at).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-text-muted text-sm">Player ID</p>
                <p className="text-text-primary font-mono text-xs">{player.id}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
