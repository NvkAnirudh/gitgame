#!/usr/bin/env python3
"""
Load Parsed Tutorials to PostgreSQL Database
"""

import json
import os
from pathlib import Path
from typing import List, Dict
import psycopg2
from psycopg2.extras import Json, execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseLoader:
    """Load parsed tutorial data into PostgreSQL"""

    def __init__(self):
        """Initialize database connection"""
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DATABASE_HOST', 'localhost'),
                port=os.getenv('DATABASE_PORT', '5432'),
                database=os.getenv('DATABASE_NAME', 'gitquest'),
                user=os.getenv('DATABASE_USER', 'gitquest'),
                password=os.getenv('DATABASE_PASSWORD', 'gitquest_dev_password')
            )
            print("✅ Connected to PostgreSQL database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise

    def load_tutorials(self, parsed_dir: str = 'content/parsed'):
        """Load tutorial JSON files into database"""
        parsed_path = Path(parsed_dir)

        if not parsed_path.exists():
            print(f"❌ Directory not found: {parsed_dir}")
            return

        # Get all JSON files except summary
        tutorial_files = [f for f in parsed_path.glob('*.json') if f.name != 'summary.json']

        print(f"\n📂 Loading {len(tutorial_files)} tutorials from {parsed_dir}/")

        cursor = self.conn.cursor()
        loaded_count = 0
        skipped_count = 0

        for filepath in sorted(tutorial_files):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Prepare data for insertion
                lesson_data = {
                    'id': data['id'],
                    'filename': data['filename'],
                    'title': data['title'],
                    'level': data['level'],
                    'story_hook': None,  # Will be added in Phase 3
                    'content': Json(data['sections']),
                    'learning_objectives': Json(data.get('learning_objectives', [])),
                    'practice_prompt': data.get('practice_prompt'),
                    'git_commands': Json(data.get('git_commands_used', [])),
                    'word_count': data.get('word_count', 0),
                    'total_sections': data.get('total_sections', 0),
                }

                # Determine order_index based on level
                level_order = {'introduction': 100, 'intermediate': 200, 'advanced': 300}
                base_order = level_order.get(data['level'], 0)
                lesson_data['order_index'] = base_order + loaded_count

                # Insert into database (upsert)
                insert_query = """
                INSERT INTO lessons (
                    id, filename, title, level, order_index,
                    story_hook, content, learning_objectives,
                    practice_prompt, git_commands, word_count, total_sections
                ) VALUES (
                    %(id)s, %(filename)s, %(title)s, %(level)s, %(order_index)s,
                    %(story_hook)s, %(content)s, %(learning_objectives)s,
                    %(practice_prompt)s, %(git_commands)s, %(word_count)s, %(total_sections)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    filename = EXCLUDED.filename,
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    learning_objectives = EXCLUDED.learning_objectives,
                    practice_prompt = EXCLUDED.practice_prompt,
                    git_commands = EXCLUDED.git_commands,
                    word_count = EXCLUDED.word_count,
                    total_sections = EXCLUDED.total_sections,
                    updated_at = NOW()
                """

                cursor.execute(insert_query, lesson_data)
                loaded_count += 1
                print(f"  ✅ {data['id']}")

            except Exception as e:
                print(f"  ❌ {filepath.name}: {e}")
                skipped_count += 1

        # Commit transaction
        self.conn.commit()
        cursor.close()

        print(f"\n📊 Load Summary:")
        print(f"  • Loaded: {loaded_count} tutorials")
        print(f"  • Skipped: {skipped_count} tutorials")

    def load_git_commands(self, parsed_dir: str = 'content/parsed'):
        """Extract and load unique Git commands into git_commands table"""
        summary_path = Path(parsed_dir) / 'summary.json'

        if not summary_path.exists():
            print(f"❌ Summary file not found: {summary_path}")
            return

        with open(summary_path, 'r') as f:
            summary = json.load(f)

        git_commands = summary.get('git_commands', [])

        print(f"\n📂 Loading {len(git_commands)} Git commands...")

        cursor = self.conn.cursor()
        loaded_count = 0

        # Category mapping based on command
        categories = {
            'init': 'repository', 'clone': 'repository',
            'add': 'staging', 'commit': 'staging', 'reset': 'staging',
            'status': 'information', 'log': 'information', 'show': 'information', 'diff': 'information',
            'branch': 'branching', 'checkout': 'branching', 'switch': 'branching', 'merge': 'branching',
            'rebase': 'advanced', 'cherry-pick': 'advanced', 'reflog': 'advanced', 'bisect': 'advanced',
            'fetch': 'remote', 'pull': 'remote', 'push': 'remote', 'remote': 'remote',
            'stash': 'workflow', 'tag': 'workflow',
            'submodule': 'advanced', 'worktree': 'advanced', 'lfs': 'advanced', 'filter-repo': 'advanced'
        }

        # Difficulty mapping
        difficulty_map = {
            'introduction': 1, 'intermediate': 3, 'advanced': 5
        }

        for cmd in git_commands:
            try:
                # Parse command to get base command
                base_cmd = cmd.replace('git ', '').split()[0] if 'git ' in cmd else cmd

                # Determine category and difficulty
                category = categories.get(base_cmd, 'other')
                difficulty = 3 if category == 'advanced' else (2 if category == 'intermediate' else 1)

                command_data = {
                    'id': base_cmd.replace(' ', '-'),
                    'command': cmd,
                    'category': category,
                    'difficulty': difficulty,
                    'description': f'{cmd} command',
                    'syntax': cmd,
                    'examples': Json([]),
                    'common_mistakes': Json([]),
                    'related_commands': Json([])
                }

                insert_query = """
                INSERT INTO git_commands (
                    id, command, syntax, description, category, difficulty,
                    examples, common_mistakes, related_commands
                ) VALUES (
                    %(id)s, %(command)s, %(syntax)s, %(description)s,
                    %(category)s, %(difficulty)s, %(examples)s,
                    %(common_mistakes)s, %(related_commands)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    command = EXCLUDED.command,
                    category = EXCLUDED.category,
                    difficulty = EXCLUDED.difficulty
                """

                cursor.execute(insert_query, command_data)
                loaded_count += 1

            except Exception as e:
                print(f"  ❌ {cmd}: {e}")

        self.conn.commit()
        cursor.close()

        print(f"  ✅ Loaded {loaded_count} Git commands")

    def print_stats(self):
        """Print database statistics"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT level, COUNT(*) FROM lessons GROUP BY level ORDER BY level")
        lesson_stats = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM git_commands")
        command_count = cursor.fetchone()[0]

        print("\n" + "="*60)
        print("📊 DATABASE STATISTICS")
        print("="*60)
        print("Lessons by Level:")
        for level, count in lesson_stats:
            print(f"  • {level.capitalize()}: {count} lessons")

        print(f"\nGit Commands: {command_count}")
        print("="*60)

        cursor.close()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("\n✅ Database connection closed")


def main():
    """Main execution"""
    print("🚀 Git Quest Database Loader")
    print("="*60)

    try:
        loader = DatabaseLoader()

        # Load tutorials
        loader.load_tutorials()

        # Load Git commands
        loader.load_git_commands()

        # Print stats
        loader.print_stats()

        # Close connection
        loader.close()

        print("\n✅ Database loading complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == '__main__':
    main()
