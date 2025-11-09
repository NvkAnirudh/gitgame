-- Git Quest Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- AUTHENTICATION TABLES
-- ============================================================================

-- Users (Authentication)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Password Reset Tokens
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);

-- Refresh Tokens (for JWT)
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    revoked BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);

-- ============================================================================
-- GAME PROFILE TABLES
-- ============================================================================

-- Players (Game Profile)
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    current_level VARCHAR(20) DEFAULT 'introduction',
    total_xp INTEGER DEFAULT 0,
    UNIQUE(user_id)
);

CREATE INDEX idx_players_user_id ON players(user_id);
CREATE INDEX idx_players_total_xp ON players(total_xp DESC);

-- ============================================================================
-- CONTENT TABLES
-- ============================================================================

-- Lessons
CREATE TABLE lessons (
    id VARCHAR(50) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    level VARCHAR(20) NOT NULL CHECK (level IN ('introduction', 'intermediate', 'advanced')),
    order_index INTEGER,
    story_hook TEXT,
    content JSONB NOT NULL,
    learning_objectives JSONB,
    practice_prompt TEXT,
    git_commands JSONB,
    word_count INTEGER,
    total_sections INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_lessons_level ON lessons(level);
CREATE INDEX idx_lessons_order_index ON lessons(order_index);

-- Git Commands Reference
CREATE TABLE git_commands (
    id VARCHAR(50) PRIMARY KEY,
    command VARCHAR(100) UNIQUE NOT NULL,
    syntax TEXT,
    description TEXT,
    category VARCHAR(50),
    difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
    examples JSONB,
    common_mistakes JSONB,
    related_commands JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_git_commands_category ON git_commands(category);
CREATE INDEX idx_git_commands_difficulty ON git_commands(difficulty);

-- Challenges
CREATE TABLE challenges (
    id VARCHAR(50) PRIMARY KEY,
    lesson_id VARCHAR(50) REFERENCES lessons(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('crisis', 'command_mastery', 'quiz', 'speed_run', 'boss')) NOT NULL,
    difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
    scenario TEXT NOT NULL,
    success_criteria JSONB NOT NULL,
    hints JSONB,
    time_limit_seconds INTEGER,
    max_score INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_challenges_lesson_id ON challenges(lesson_id);
CREATE INDEX idx_challenges_type ON challenges(type);
CREATE INDEX idx_challenges_difficulty ON challenges(difficulty);

-- Achievements
CREATE TABLE achievements (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    badge_icon VARCHAR(255),
    category VARCHAR(50),
    unlock_criteria JSONB NOT NULL,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_achievements_category ON achievements(category);

-- ============================================================================
-- PLAYER PROGRESS TABLES
-- ============================================================================

-- Player Progress (Lesson Completion)
CREATE TABLE player_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    lesson_id VARCHAR(50) REFERENCES lessons(id) ON DELETE CASCADE,
    status VARCHAR(20) CHECK (status IN ('not_started', 'in_progress', 'completed')) DEFAULT 'not_started',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    time_spent_seconds INTEGER DEFAULT 0,
    score INTEGER,
    attempts INTEGER DEFAULT 0,
    UNIQUE(player_id, lesson_id)
);

CREATE INDEX idx_player_progress_player_id ON player_progress(player_id);
CREATE INDEX idx_player_progress_lesson_id ON player_progress(lesson_id);
CREATE INDEX idx_player_progress_status ON player_progress(status);

-- Challenge Attempts
CREATE TABLE challenge_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    challenge_id VARCHAR(50) REFERENCES challenges(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    success BOOLEAN DEFAULT FALSE,
    commands_used JSONB,
    score INTEGER DEFAULT 0,
    time_taken_seconds INTEGER,
    hints_used INTEGER DEFAULT 0
);

CREATE INDEX idx_challenge_attempts_player_id ON challenge_attempts(player_id);
CREATE INDEX idx_challenge_attempts_challenge_id ON challenge_attempts(challenge_id);
CREATE INDEX idx_challenge_attempts_success ON challenge_attempts(success);

-- Player Achievements
CREATE TABLE player_achievements (
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    achievement_id VARCHAR(50) REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (player_id, achievement_id)
);

CREATE INDEX idx_player_achievements_player_id ON player_achievements(player_id);

-- ============================================================================
-- ANALYTICS TABLES
-- ============================================================================

-- Player Events (for analytics and tracking)
CREATE TABLE player_events (
    id BIGSERIAL PRIMARY KEY,
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    session_id UUID,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_player_events_player_id ON player_events(player_id);
CREATE INDEX idx_player_events_session_id ON player_events(session_id);
CREATE INDEX idx_player_events_event_type ON player_events(event_type);
CREATE INDEX idx_player_events_timestamp ON player_events(timestamp DESC);

-- Game Sessions
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    lessons_completed INTEGER DEFAULT 0,
    challenges_completed INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0
);

CREATE INDEX idx_game_sessions_player_id ON game_sessions(player_id);
CREATE INDEX idx_game_sessions_started_at ON game_sessions(started_at DESC);

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- Leaderboard View
CREATE OR REPLACE VIEW leaderboard AS
SELECT
    p.id,
    p.username,
    p.display_name,
    p.total_xp,
    p.current_level,
    COUNT(DISTINCT pp.lesson_id) FILTER (WHERE pp.status = 'completed') as lessons_completed,
    COUNT(DISTINCT pa.achievement_id) as achievements_count,
    RANK() OVER (ORDER BY p.total_xp DESC) as rank
FROM players p
LEFT JOIN player_progress pp ON p.id = pp.player_id
LEFT JOIN player_achievements pa ON p.id = pa.player_id
WHERE p.user_id IN (SELECT id FROM users WHERE is_active = TRUE)
GROUP BY p.id, p.username, p.display_name, p.total_xp, p.current_level
ORDER BY p.total_xp DESC;

-- Player Stats View
CREATE OR REPLACE VIEW player_stats AS
SELECT
    p.id as player_id,
    p.username,
    p.total_xp,
    p.current_level,
    COUNT(DISTINCT pp.lesson_id) FILTER (WHERE pp.status = 'completed') as lessons_completed,
    COUNT(DISTINCT pp.lesson_id) FILTER (WHERE pp.status = 'in_progress') as lessons_in_progress,
    COUNT(DISTINCT ca.challenge_id) FILTER (WHERE ca.success = TRUE) as challenges_completed,
    COUNT(DISTINCT pa.achievement_id) as achievements_unlocked,
    AVG(ca.score) FILTER (WHERE ca.success = TRUE) as avg_challenge_score,
    SUM(pp.time_spent_seconds) as total_learning_time_seconds
FROM players p
LEFT JOIN player_progress pp ON p.id = pp.player_id
LEFT JOIN challenge_attempts ca ON p.id = ca.player_id
LEFT JOIN player_achievements pa ON p.id = pa.player_id
GROUP BY p.id, p.username, p.total_xp, p.current_level;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for lessons table
CREATE TRIGGER update_lessons_updated_at BEFORE UPDATE ON lessons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA / SEED
-- ============================================================================

-- Insert default achievements
INSERT INTO achievements (id, name, description, category, unlock_criteria, points) VALUES
('first-commit', 'First Commit', 'Made your first Git commit', 'introduction', '{"type": "lesson_completed", "lesson_id": "introduction-staging-and-committing-files"}', 10),
('merge-master', 'Merge Master', 'Successfully resolved 10 merge conflicts', 'intermediate', '{"type": "challenges_completed", "count": 10, "category": "merge"}', 50),
('time-traveler', 'Time Traveler', 'Used git reflog to recover lost work', 'advanced', '{"type": "lesson_completed", "lesson_id": "advanced-git-reflog"}', 100),
('command-ninja', 'Command Ninja', 'Completed 25 challenges', 'general', '{"type": "total_challenges", "count": 25}', 75),
('speed-demon', 'Speed Demon', 'Completed a speed run challenge in under 60 seconds', 'challenge', '{"type": "speed_run", "time_limit": 60}', 50);

-- Grant permissions (adjust based on your DB user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gitquest_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gitquest_user;
