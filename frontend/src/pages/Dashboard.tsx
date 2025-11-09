import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { usePlayerStore } from '../stores/playerStore';
import { lessonsService } from '../services/lessons';
import type { LessonListItem } from '../types/api';

export default function Dashboard() {
  const { user, logout } = useAuthStore();
  const { player, stats, loadPlayer, loadStats } = usePlayerStore();
  const [lessons, setLessons] = useState<LessonListItem[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        loadPlayer(),
        loadStats(),
        loadLessons(),
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadLessons = async (level?: string) => {
    try {
      const data = await lessonsService.getLessons(level === 'all' ? undefined : level);
      setLessons(data);
    } catch (error) {
      console.error('Failed to load lessons:', error);
    }
  };

  const handleLevelFilter = (level: string) => {
    setSelectedLevel(level);
    loadLessons(level);
  };

  const getLevelBadge = (level: string) => {
    const badges = {
      introduction: 'badge-cyan',
      intermediate: 'badge-purple',
      advanced: 'badge-orange',
    };
    return badges[level as keyof typeof badges] || 'badge-cyan';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-neon-cyan text-2xl">
          <span className="loading-dots">loading</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen grid-pattern">
      {/* Header */}
      <header className="bg-cyber-black/80 border-b border-neon-cyan/30 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-3xl font-bold heading-neon text-glow">
            GIT QUEST
          </h1>

          <div className="flex items-center gap-6">
            {player && (
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-text-primary font-semibold">
                    {player.display_name || player.username}
                  </p>
                  <p className="text-text-muted text-sm">
                    {player.current_level}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-neon-green text-2xl font-bold">
                    {player.total_xp}
                  </span>
                  <span className="text-text-secondary text-sm">XP</span>
                </div>
              </div>
            )}
            <button
              onClick={logout}
              className="btn btn-ghost text-sm"
            >
              logout
            </button>
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      {stats && (
        <div className="bg-cyber-black/60 border-b border-neon-cyan/20">
          <div className="max-w-7xl mx-auto px-4 py-3 flex gap-6">
            <div className="flex items-center gap-2">
              <span className="text-neon-cyan">✓</span>
              <span className="text-text-secondary text-sm">
                {stats.lessons_completed} lessons completed
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-electric-purple">⚡</span>
              <span className="text-text-secondary text-sm">
                {stats.lessons_in_progress} in progress
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-neon-green">★</span>
              <span className="text-text-secondary text-sm">
                {stats.achievements_unlocked} achievements
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Level Filter */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold heading-purple mb-4">
            {'>'} select your path
          </h2>
          <div className="flex gap-3">
            {['all', 'introduction', 'intermediate', 'advanced'].map((level) => (
              <button
                key={level}
                onClick={() => handleLevelFilter(level)}
                className={`btn ${
                  selectedLevel === level ? 'btn-primary' : 'btn-ghost'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Lessons Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {lessons.map((lesson) => (
            <Link
              key={lesson.id}
              to={`/lesson/${lesson.id}`}
              className="card-hover group"
            >
              <div className="flex items-start justify-between mb-3">
                <span className="text-text-muted text-sm">
                  #{lesson.order_index?.toString().padStart(2, '0')}
                </span>
                <span className={`badge ${getLevelBadge(lesson.level)}`}>
                  {lesson.level}
                </span>
              </div>

              <h3 className="text-xl font-bold text-neon-cyan group-hover:text-glow mb-2 transition-all">
                {lesson.title}
              </h3>

              <div className="flex items-center gap-2 text-text-secondary text-sm mb-3">
                <span>{lesson.total_sections} sections</span>
                <span>•</span>
                <span>{lesson.git_commands?.length || 0} commands</span>
              </div>

              {lesson.git_commands && lesson.git_commands.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {lesson.git_commands.slice(0, 3).map((cmd, idx) => (
                    <code
                      key={idx}
                      className="text-xs bg-neon-green/10 text-neon-green px-2 py-1 rounded border border-neon-green/30"
                    >
                      {cmd}
                    </code>
                  ))}
                  {lesson.git_commands.length > 3 && (
                    <span className="text-xs text-text-muted">
                      +{lesson.git_commands.length - 3} more
                    </span>
                  )}
                </div>
              )}
            </Link>
          ))}
        </div>

        {lessons.length === 0 && (
          <div className="text-center py-12">
            <p className="text-text-secondary text-lg">
              no lessons found for this level
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
