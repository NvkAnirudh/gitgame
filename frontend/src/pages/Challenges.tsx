import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { challengesService, type ChallengeListItem, type Challenge, type ChallengeAttempt } from '../services/challenges';
import { storyService, type MentorTip } from '../services/story';

export default function Challenges() {
  const { lessonId } = useParams<{ lessonId?: string }>();
  const [challenges, setChallenges] = useState<ChallengeListItem[]>([]);
  const [selectedChallenge, setSelectedChallenge] = useState<Challenge | null>(null);
  const [mentorTip, setMentorTip] = useState<MentorTip | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeAttempt, setActiveAttempt] = useState<ChallengeAttempt | null>(null);
  const [commandInput, setCommandInput] = useState('');
  const [executedCommands, setExecutedCommands] = useState<string[]>([]);
  const [startTime, setStartTime] = useState<number | null>(null);

  useEffect(() => {
    loadChallenges();
  }, [lessonId]);

  const loadChallenges = async () => {
    setIsLoading(true);
    try {
      const data = await challengesService.getChallenges(
        lessonId ? { lesson_id: lessonId } : undefined
      );
      setChallenges(data);
    } catch (error) {
      console.error('Failed to load challenges:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadChallengeDetails = async (challengeId: string) => {
    try {
      const challenge = await challengesService.getChallenge(challengeId);
      setSelectedChallenge(challenge);

      // Load mentor tip if challenge has lesson_id
      if (challenge.lesson_id) {
        try {
          const tip = await storyService.getMentorTip(challenge.lesson_id);
          setMentorTip(tip);
        } catch (e) {
          console.error('Failed to load mentor tip:', e);
        }
      }
    } catch (error) {
      console.error('Failed to load challenge:', error);
    }
  };

  const handleStartChallenge = async () => {
    if (!selectedChallenge) return;

    try {
      const attempt = await challengesService.startChallenge(selectedChallenge.id);
      setActiveAttempt(attempt);
      setStartTime(Date.now());
      setExecutedCommands([]);
    } catch (error) {
      console.error('Failed to start challenge:', error);
      alert('Failed to start challenge. Please try again.');
    }
  };

  const handleExecuteCommand = () => {
    if (!commandInput.trim()) return;
    setExecutedCommands([...executedCommands, commandInput.trim()]);
    setCommandInput('');
  };

  const handleSubmitChallenge = async () => {
    if (!selectedChallenge || !activeAttempt || !startTime) return;

    const timeTaken = Math.floor((Date.now() - startTime) / 1000);

    try {
      const result = await challengesService.submitChallenge(selectedChallenge.id, {
        commands_used: executedCommands,
        time_taken_seconds: timeTaken,
        hints_used: 0,
      });

      alert(result.feedback || (result.success ? 'Challenge completed!' : 'Challenge incomplete.'));
      setActiveAttempt(null);
      setStartTime(null);
      setExecutedCommands([]);
    } catch (error) {
      console.error('Failed to submit challenge:', error);
      alert('Failed to submit challenge. Please try again.');
    }
  };

  const getTypeIcon = (type: string) => {
    const icons = {
      crisis: '🚨',
      command_mastery: '⚔️',
      quiz: '📝',
      speed_run: '⚡',
      boss: '👾',
    };
    return icons[type as keyof typeof icons] || '🎯';
  };

  const getDifficultyStars = (difficulty?: number) => {
    if (!difficulty) return null;
    return '⭐'.repeat(difficulty);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-neon-green">Loading challenges...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cyber-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-neon-green">
            {lessonId ? 'Lesson Challenges' : 'All Challenges'}
          </h1>
          <Link
            to="/dashboard"
            className="px-4 py-2 bg-neon-green/20 text-neon-green rounded hover:bg-neon-green/30 transition"
          >
            ← Back to Dashboard
          </Link>
        </div>

        {!selectedChallenge ? (
          // Challenge List
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {challenges.map((challenge) => (
              <div
                key={challenge.id}
                className="bg-cyber-gray border border-neon-green/30 rounded-lg p-6 hover:border-neon-green transition cursor-pointer"
                onClick={() => loadChallengeDetails(challenge.id)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="text-4xl">{getTypeIcon(challenge.type)}</div>
                  <div className="text-neon-purple text-sm">
                    {challenge.max_score} XP
                  </div>
                </div>
                <h3 className="text-xl font-bold mb-2">{challenge.title}</h3>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <span className="capitalize">{challenge.type.replace('_', ' ')}</span>
                  {challenge.difficulty && (
                    <>
                      <span>•</span>
                      <span>{getDifficultyStars(challenge.difficulty)}</span>
                    </>
                  )}
                </div>
                {challenge.time_limit_seconds && (
                  <div className="mt-2 text-sm text-neon-cyan">
                    ⏱️ {challenge.time_limit_seconds}s limit
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          // Challenge Details
          <div className="bg-cyber-gray border border-neon-green/30 rounded-lg p-8">
            <button
              onClick={() => {
                setSelectedChallenge(null);
                setMentorTip(null);
                setActiveAttempt(null);
              }}
              className="mb-6 text-neon-green hover:underline"
            >
              ← Back to Challenges
            </button>

            <div className="flex items-start justify-between mb-6">
              <h2 className="text-3xl font-bold">{selectedChallenge.title}</h2>
              <div className="text-2xl">{getTypeIcon(selectedChallenge.type)}</div>
            </div>

            {mentorTip && (
              <div className="bg-neon-cyan/10 border border-neon-cyan/30 rounded p-4 mb-6">
                <div className="flex items-start gap-3">
                  <div className="text-3xl">💡</div>
                  <div>
                    <div className="font-bold text-neon-cyan mb-1">
                      {mentorTip.character.name} says:
                    </div>
                    <div className="text-gray-300">{mentorTip.tip}</div>
                  </div>
                </div>
              </div>
            )}

            <div className="mb-6">
              <h3 className="text-xl font-bold mb-2 text-neon-purple">Scenario</h3>
              <p className="text-gray-300 whitespace-pre-line">{selectedChallenge.scenario}</p>
            </div>

            {!activeAttempt ? (
              <button
                onClick={handleStartChallenge}
                className="w-full py-3 bg-neon-green text-cyber-black font-bold rounded hover:bg-neon-green/90 transition"
              >
                Start Challenge
              </button>
            ) : (
              <div>
                <div className="mb-4">
                  <h3 className="text-xl font-bold mb-2 text-neon-cyan">Execute Commands</h3>
                  <div className="bg-black/50 border border-neon-green/30 rounded p-4 mb-2 min-h-[200px]">
                    {executedCommands.length === 0 ? (
                      <div className="text-gray-500">Execute commands to solve the challenge...</div>
                    ) : (
                      executedCommands.map((cmd, idx) => (
                        <div key={idx} className="text-neon-green mb-1">
                          $ {cmd}
                        </div>
                      ))
                    )}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={commandInput}
                      onChange={(e) => setCommandInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleExecuteCommand()}
                      placeholder="Type git command..."
                      className="flex-1 px-4 py-2 bg-cyber-black border border-neon-green/30 rounded text-neon-green focus:border-neon-green focus:outline-none"
                    />
                    <button
                      onClick={handleExecuteCommand}
                      className="px-6 py-2 bg-neon-cyan text-cyber-black font-bold rounded hover:bg-neon-cyan/90"
                    >
                      Execute
                    </button>
                  </div>
                </div>

                <button
                  onClick={handleSubmitChallenge}
                  disabled={executedCommands.length === 0}
                  className="w-full py-3 bg-neon-green text-cyber-black font-bold rounded hover:bg-neon-green/90 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Submit Solution
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
