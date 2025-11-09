"""
Load generated curriculum lessons into the database
Replaces old transcript-based content with story-driven lessons
"""

import os
import json
from pathlib import Path
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# Load environment variables
root_dir = Path(__file__).parent.parent.parent
env_file = root_dir / ".env"
load_dotenv(dotenv_path=env_file)


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv("DATABASE_HOST", "localhost"),
        port=int(os.getenv("DATABASE_PORT", "5432")),
        database=os.getenv("DATABASE_NAME", "gitquest"),
        user=os.getenv("DATABASE_USER", "gitquest"),
        password=os.getenv("DATABASE_PASSWORD", "gitquest_dev_password")
    )


def load_generated_lessons(lessons_dir: str):
    """
    Load all generated lessons from JSON files into database

    Args:
        lessons_dir: Path to directory with generated lesson JSON files
    """
    lessons_path = Path(lessons_dir)

    if not lessons_path.exists():
        print(f"❌ Error: Directory not found: {lessons_dir}")
        return

    lesson_files = sorted(lessons_path.glob("*.json"))

    if not lesson_files:
        print(f"❌ Error: No lesson JSON files found in {lessons_dir}")
        return

    print(f"\n{'='*60}")
    print(f"Loading {len(lesson_files)} lessons into database")
    print(f"{'='*60}\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    loaded_count = 0
    updated_count = 0
    error_count = 0

    for lesson_file in lesson_files:
        try:
            # Read lesson JSON
            with open(lesson_file, 'r', encoding='utf-8') as f:
                lesson_data = json.load(f)

            lesson_id = lesson_data['id']

            # Check if lesson exists
            cursor.execute("SELECT id FROM lessons WHERE id = %s", (lesson_id,))
            exists = cursor.fetchone()

            if exists:
                # Update existing lesson
                cursor.execute("""
                    UPDATE lessons SET
                        filename = %s,
                        title = %s,
                        level = %s,
                        order_index = %s,
                        story_hook = %s,
                        content = %s,
                        learning_objectives = %s,
                        practice_prompt = %s,
                        git_commands = %s,
                        word_count = %s,
                        total_sections = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """, (
                    lesson_data['filename'],
                    lesson_data['title'],
                    lesson_data['level'],
                    lesson_data['order_index'],
                    lesson_data.get('story_hook'),
                    Json(lesson_data.get('sections', [])),
                    Json(lesson_data.get('learning_objectives', [])),
                    lesson_data.get('practice_challenge'),
                    Json(lesson_data.get('git_commands', [])),
                    lesson_data.get('word_count', 0),
                    len(lesson_data.get('sections', [])),
                    lesson_id
                ))
                updated_count += 1
                print(f"✓ Updated: {lesson_data['title']}")

            else:
                # Insert new lesson
                cursor.execute("""
                    INSERT INTO lessons (
                        id, filename, title, level, order_index,
                        story_hook, content, learning_objectives, practice_prompt,
                        git_commands, word_count, total_sections
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    lesson_id,
                    lesson_data['filename'],
                    lesson_data['title'],
                    lesson_data['level'],
                    lesson_data['order_index'],
                    lesson_data.get('story_hook'),
                    Json(lesson_data.get('sections', [])),
                    Json(lesson_data.get('learning_objectives', [])),
                    lesson_data.get('practice_challenge'),
                    Json(lesson_data.get('git_commands', [])),
                    lesson_data.get('word_count', 0),
                    len(lesson_data.get('sections', []))
                ))
                loaded_count += 1
                print(f"✓ Inserted: {lesson_data['title']}")

            # Create/update challenge if crisis_scenario exists
            if 'crisis_scenario' in lesson_data:
                create_challenge(cursor, lesson_id, lesson_data['crisis_scenario'])

            conn.commit()

        except Exception as e:
            print(f"✗ Error loading {lesson_file.name}: {e}")
            error_count += 1
            conn.rollback()
            continue

    cursor.close()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Database Load Complete!")
    print(f"{'='*60}")
    print(f"  Inserted: {loaded_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {loaded_count + updated_count}")
    print(f"{'='*60}\n")


def create_challenge(cursor, lesson_id: str, crisis_data: dict):
    """Create or update a challenge from crisis scenario data"""

    challenge_id = f"{lesson_id}_crisis"

    # Check if challenge exists
    cursor.execute("SELECT id FROM challenges WHERE id = %s", (challenge_id,))
    exists = cursor.fetchone()

    success_criteria = {
        "required_commands": crisis_data.get('required_commands', []),
        "description": crisis_data.get('success_criteria', '')
    }

    if exists:
        cursor.execute("""
            UPDATE challenges SET
                title = %s,
                type = %s,
                scenario = %s,
                success_criteria = %s,
                max_score = %s
            WHERE id = %s
        """, (
            crisis_data.get('title', 'Crisis Challenge'),
            'crisis',
            crisis_data.get('description', ''),
            Json(success_criteria),
            crisis_data.get('xp_reward', 50),
            challenge_id
        ))
    else:
        cursor.execute("""
            INSERT INTO challenges (
                id, lesson_id, title, type, scenario, success_criteria, max_score
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            challenge_id,
            lesson_id,
            crisis_data.get('title', 'Crisis Challenge'),
            'crisis',
            crisis_data.get('description', ''),
            Json(success_criteria),
            crisis_data.get('xp_reward', 50)
        ))


if __name__ == "__main__":
    print("🎮 Git Quest - Load Generated Curriculum")
    print("=" * 60)

    # Path to generated lessons
    lessons_dir = str(Path(__file__).parent.parent / "generated_lessons")

    # Check if directory exists
    if not Path(lessons_dir).exists():
        print(f"\n❌ Generated lessons directory not found: {lessons_dir}")
        print("\nPlease run the curriculum generator first:")
        print("  python data-pipeline/scripts/generate_curriculum.py")
        exit(1)

    # Load lessons
    load_generated_lessons(lessons_dir)

    print("✨ All lessons loaded successfully!")
    print("\nYou can now:")
    print("  1. Start the backend: cd backend && ./run.sh")
    print("  2. View lessons at: http://localhost:8000/api/lessons/")
    print("  3. Start the frontend: cd frontend && npm run dev")
