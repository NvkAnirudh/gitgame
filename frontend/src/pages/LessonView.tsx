import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { lessonsService } from '../services/lessons';
import type { Lesson, LessonSection } from '../types/api';
import Terminal from '../components/terminal/Terminal';

export default function LessonView() {
  const { lessonId } = useParams<{ lessonId: string }>();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentSection, setCurrentSection] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (lessonId) {
      loadLesson(lessonId);
    }
  }, [lessonId]);

  const loadLesson = async (id: string) => {
    setIsLoading(true);
    try {
      const data = await lessonsService.getLesson(id);
      setLesson(data);
      await lessonsService.startLesson(id);
    } catch (error) {
      console.error('Failed to load lesson:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    if (lesson && currentSection < lesson.content.length - 1) {
      setCurrentSection(currentSection + 1);
    }
  };

  const handlePrevious = () => {
    if (currentSection > 0) {
      setCurrentSection(currentSection - 1);
    }
  };

  const handleComplete = async () => {
    if (!lesson || !lessonId) return;

    const timeSpent = Math.floor((Date.now() - startTime) / 1000);
    try {
      await lessonsService.completeLesson(lessonId, timeSpent);
      alert('Lesson completed! +50 XP');
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Failed to complete lesson:', error);
    }
  };

  const renderSection = (section: LessonSection) => {
    switch (section.type) {
      case 'dialogue':
        return (
          <div className="bg-electric-purple/5 border-l-4 border-electric-purple p-4 rounded mb-4">
            {section.speaker && (
              <p className="text-electric-purple font-bold mb-2 text-sm">
                {section.speaker}:
              </p>
            )}
            <p className="text-text-primary leading-relaxed text-sm">{section.content}</p>
          </div>
        );

      case 'explanation':
        return (
          <div className="bg-neon-cyan/5 border-l-4 border-neon-cyan p-4 rounded mb-4">
            <p className="text-text-primary leading-relaxed text-sm">{section.content}</p>
          </div>
        );

      case 'code':
        return (
          <div className="bg-cyber-black/80 border border-neon-green/30 p-4 rounded mb-4">
            <pre className="text-neon-green text-xs overflow-x-auto">
              <code>{section.content}</code>
            </pre>
          </div>
        );

      case 'tip':
        return (
          <div className="bg-neon-orange/5 border-l-4 border-neon-orange p-4 rounded mb-4">
            <p className="text-neon-orange font-bold mb-2 text-sm">💡 Tip:</p>
            <p className="text-text-primary leading-relaxed text-sm">{section.content}</p>
          </div>
        );

      default:
        return <p className="text-text-primary text-sm mb-4">{section.content}</p>;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-neon-cyan text-2xl">Loading lesson...</div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-neon-red text-xl mb-4">Lesson not found</p>
          <Link to="/dashboard" className="px-4 py-2 bg-neon-green text-cyber-black rounded">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const currentSectionData = lesson.content[currentSection];
  const isLastSection = currentSection === lesson.content.length - 1;

  return (
    <div className="min-h-screen bg-cyber-black text-white">
      {/* Header */}
      <header className="bg-cyber-gray border-b border-neon-cyan/30 sticky top-0 z-10">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <Link to="/dashboard" className="text-neon-cyan hover:underline text-sm mb-2 inline-block">
                ← Back to Dashboard
              </Link>
              <h1 className="text-2xl font-bold text-neon-green">{lesson.title}</h1>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">
                Section {currentSection + 1} / {lesson.content.length}
              </div>
              <div className="w-48 bg-cyber-black/50 rounded-full h-2 mt-1">
                <div
                  className="bg-neon-cyan h-2 rounded-full transition-all"
                  style={{ width: `${((currentSection + 1) / lesson.content.length) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Split Layout: Content Left | Terminal Right */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* LEFT PANEL: Lesson Content */}
        <div className="w-1/2 overflow-y-auto border-r border-neon-green/30 p-6">
          {/* Story Hook */}
          {currentSection === 0 && lesson.story_hook && (
            <div className="mb-6 bg-electric-purple/10 border border-electric-purple/30 p-4 rounded">
              <h2 className="text-lg font-bold text-electric-purple mb-2">
                Mission Briefing
              </h2>
              <p className="text-sm text-gray-300">{lesson.story_hook}</p>
            </div>
          )}

          {/* Current Section Content */}
          <div className="mb-6">
            {renderSection(currentSectionData)}
          </div>

          {/* Learning Objectives */}
          {lesson.learning_objectives && lesson.learning_objectives.length > 0 && (
            <div className="mb-6 bg-neon-cyan/10 border border-neon-cyan/30 p-4 rounded">
              <h3 className="text-md font-bold text-neon-cyan mb-3">Learning Objectives</h3>
              <ul className="space-y-2">
                {lesson.learning_objectives.map((obj, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm">
                    <span className="text-neon-green">✓</span>
                    <span className="text-gray-300">{obj}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Git Commands */}
          {lesson.git_commands && lesson.git_commands.length > 0 && (
            <div className="mb-6 bg-cyber-black/80 border border-neon-green/30 p-4 rounded">
              <h3 className="text-md font-bold text-neon-green mb-3">Git Commands</h3>
              <div className="space-y-2">
                {lesson.git_commands.map((cmd, idx) => (
                  <code
                    key={idx}
                    className="block bg-cyber-black text-neon-green px-3 py-1 rounded text-xs"
                  >
                    {cmd}
                  </code>
                ))}
              </div>
            </div>
          )}

          {/* Practice Challenge */}
          {lesson.practice_prompt && (
            <div className="mb-6 bg-neon-green/10 border border-neon-green/30 p-4 rounded">
              <h3 className="text-md font-bold text-neon-green mb-2">Practice Challenge</h3>
              <p className="text-sm text-gray-300 leading-relaxed">{lesson.practice_prompt}</p>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between items-center mt-8 pt-4 border-t border-gray-700">
            <button
              onClick={handlePrevious}
              disabled={currentSection === 0}
              className="px-4 py-2 bg-neon-cyan/20 text-neon-cyan rounded hover:bg-neon-cyan/30 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              ← Previous
            </button>

            <div className="flex gap-1">
              {lesson.content.map((_, idx) => (
                <div
                  key={idx}
                  className={`w-2 h-2 rounded-full ${
                    idx === currentSection
                      ? 'bg-neon-cyan'
                      : idx < currentSection
                      ? 'bg-neon-green'
                      : 'bg-gray-600'
                  }`}
                />
              ))}
            </div>

            {isLastSection ? (
              <button
                onClick={handleComplete}
                className="px-6 py-2 bg-neon-green text-cyber-black font-bold rounded hover:bg-neon-green/90"
              >
                Complete Lesson →
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="px-4 py-2 bg-neon-green/20 text-neon-green rounded hover:bg-neon-green/30"
              >
                Next →
              </button>
            )}
          </div>
        </div>

        {/* RIGHT PANEL: Interactive Terminal */}
        <div className="w-1/2 bg-cyber-black p-4 flex flex-col">
          <div className="mb-3">
            <h3 className="text-lg font-bold text-neon-green">Interactive Workspace</h3>
            <p className="text-xs text-gray-400 mt-1">
              Practice Git commands in real-time. Try the commands shown on the left!
            </p>
          </div>
          <div className="flex-1 border border-neon-green/30 rounded overflow-hidden">
            <Terminal lessonId={lessonId} />
          </div>
        </div>
      </div>
    </div>
  );
}
