import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { lessonsService } from '../services/lessons';
import type { Lesson, LessonSection } from '../types/api';

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

      // Start the lesson
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
          <div className="bg-electric-purple/5 border-l-4 border-electric-purple p-6 rounded">
            {section.speaker && (
              <p className="text-electric-purple font-bold mb-2">
                {section.speaker}:
              </p>
            )}
            <p className="text-text-primary leading-relaxed">{section.content}</p>
          </div>
        );

      case 'explanation':
        return (
          <div className="bg-neon-cyan/5 border-l-4 border-neon-cyan p-6 rounded">
            <p className="text-text-primary leading-relaxed">{section.content}</p>
          </div>
        );

      case 'code':
        return (
          <div className="bg-cyber-black/80 border border-neon-green/30 p-6 rounded">
            <pre className="terminal-text overflow-x-auto">
              <code>{section.content}</code>
            </pre>
          </div>
        );

      case 'tip':
        return (
          <div className="bg-neon-orange/5 border-l-4 border-neon-orange p-6 rounded">
            <p className="text-neon-orange font-bold mb-2">💡 Tip:</p>
            <p className="text-text-primary leading-relaxed">{section.content}</p>
          </div>
        );

      default:
        return <p className="text-text-primary">{section.content}</p>;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-neon-cyan text-2xl">
          <span className="loading-dots">loading lesson</span>
        </div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-neon-red text-xl mb-4">Lesson not found</p>
          <Link to="/dashboard" className="btn btn-primary">
            back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  const currentSectionData = lesson.content[currentSection];
  const isLastSection = currentSection === lesson.content.length - 1;

  return (
    <div className="min-h-screen grid-pattern">
      {/* Header */}
      <header className="bg-cyber-black/80 border-b border-neon-cyan/30 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <Link to="/dashboard" className="text-text-secondary hover:text-neon-cyan mb-2 inline-block">
            ← back to dashboard
          </Link>
          <h1 className="text-3xl font-bold heading-neon text-glow">
            {lesson.title}
          </h1>
          <p className="text-text-secondary mt-1">
            Section {currentSection + 1} of {lesson.content.length}
          </p>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="bg-cyber-black/60">
        <div className="max-w-5xl mx-auto px-4 py-2">
          <div className="w-full bg-cyber-black/50 rounded-full h-2">
            <div
              className="bg-neon-cyan h-2 rounded-full transition-all duration-300"
              style={{
                width: `${((currentSection + 1) / lesson.content.length) * 100}%`,
              }}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Story Hook (only on first section) */}
        {currentSection === 0 && lesson.story_hook && (
          <div className="mb-8 card bg-electric-purple/10 border-electric-purple/30">
            <h2 className="text-xl font-bold heading-purple mb-3">
              {'>'} mission briefing
            </h2>
            <p className="text-text-primary leading-relaxed">{lesson.story_hook}</p>
          </div>
        )}

        {/* Current Section */}
        <div className="mb-8">
          {renderSection(currentSectionData)}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={handlePrevious}
            disabled={currentSection === 0}
            className="btn btn-ghost disabled:opacity-30 disabled:cursor-not-allowed"
          >
            ← previous
          </button>

          <div className="flex items-center gap-2">
            {lesson.content.map((_, idx) => (
              <div
                key={idx}
                className={`w-2 h-2 rounded-full ${
                  idx === currentSection
                    ? 'bg-neon-cyan'
                    : idx < currentSection
                    ? 'bg-neon-green'
                    : 'bg-text-muted/30'
                }`}
              />
            ))}
          </div>

          {isLastSection ? (
            <button onClick={handleComplete} className="btn btn-success">
              complete lesson →
            </button>
          ) : (
            <button onClick={handleNext} className="btn btn-primary">
              next →
            </button>
          )}
        </div>

        {/* Learning Objectives & Commands (sidebar on last section) */}
        {isLastSection && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
            {lesson.learning_objectives && (
              <div className="card">
                <h3 className="text-lg font-bold heading-cyan mb-3">
                  learning objectives
                </h3>
                <ul className="space-y-2">
                  {lesson.learning_objectives.map((obj, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-neon-green">✓</span>
                      <span className="text-text-secondary">{obj}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {lesson.git_commands && (
              <div className="card">
                <h3 className="text-lg font-bold heading-cyan mb-3">
                  git commands learned
                </h3>
                <div className="space-y-2">
                  {lesson.git_commands.map((cmd, idx) => (
                    <code
                      key={idx}
                      className="block bg-cyber-black/80 text-neon-green px-3 py-2 rounded border border-neon-green/30"
                    >
                      {cmd}
                    </code>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
