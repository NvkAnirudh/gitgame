"""
Curriculum Generator: Transform raw Git transcripts into story-driven lessons
Uses Anthropic API to generate engaging, narrative-driven content
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import anthropic
from dotenv import load_dotenv

# Load environment variables from root .env file
root_dir = Path(__file__).parent.parent.parent
env_file = root_dir / ".env"
load_dotenv(dotenv_path=env_file)


class CurriculumGenerator:
    """Transform Git tutorial transcripts into Git Quest lessons"""

    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment!\n"
                "Please add it to the .env file at the project root:\n"
                "  ANTHROPIC_API_KEY=sk-ant-api03-your-key-here\n"
                "Get your key from: https://console.anthropic.com/"
            )

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"  # Latest Sonnet model

    def generate_lesson(self, transcript_path: str, lesson_metadata: Dict) -> Dict:
        """
        Transform a transcript into a story-driven lesson

        Args:
            transcript_path: Path to the transcript file
            lesson_metadata: Metadata about the lesson (title, level, order)

        Returns:
            Structured lesson data for Git Quest
        """
        # Read transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()

        # Create the transformation prompt
        prompt = self._create_transformation_prompt(transcript, lesson_metadata)

        print(f"   Calling Anthropic API...")

        # Call Anthropic API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse the response
        response_text = message.content[0].text

        try:
            lesson_data = json.loads(response_text)
            return lesson_data
        except json.JSONDecodeError:
            # If JSON parsing fails, extract JSON from markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                raise ValueError("Failed to parse lesson data from API response")

    def _create_transformation_prompt(self, transcript: str, metadata: Dict) -> str:
        """Create the prompt for transforming transcripts into lessons"""

        return f"""You are creating an interactive lesson for "Git Quest", a story-driven Git learning game.

**Game Context:**
- Players are "Version Control Guardians" at a fictional company called "Nexus Labs"
- Each Git concept is a superpower they unlock to solve development crises
- Lessons tell engaging stories, NOT dry tutorials
- Remove ALL references to DataCamp, original speakers, or video content
- Make learning feel like an epic adventure

**Lesson Metadata:**
- Title: {metadata['title']}
- Level: {metadata['level']}
- Order: {metadata['order_index']}

**Original Transcript (knowledge base only):**
```
{transcript[:4000]}...
```

**Your Task:**
Transform this transcript into a structured lesson with the following JSON format:

```json
{{
  "story_hook": "An engaging 2-3 sentence crisis at Nexus Labs that sets up why this skill matters. Make it dramatic!",

  "learning_objectives": [
    "Clear, practical learning objective 1",
    "Clear, practical learning objective 2",
    "Clear, practical learning objective 3"
  ],

  "sections": [
    {{
      "type": "dialogue",
      "speaker": "Alex (Senior Dev)",
      "content": "Story dialogue that introduces the problem..."
    }},
    {{
      "type": "explanation",
      "content": "Clear explanation of the Git concept using simple language..."
    }},
    {{
      "type": "code",
      "content": "git command example\\n# What it does\\n$ git status"
    }},
    {{
      "type": "tip",
      "content": "Pro tip or important warning about this concept"
    }}
  ],

  "git_commands": [
    "git init",
    "git status",
    "git add"
  ],

  "practice_challenge": "A hands-on challenge: 'Your task: Initialize a repository and make your first commit...'",

  "crisis_scenario": {{
    "title": "The Merge Disaster",
    "description": "Production is down! Use what you learned to fix it.",
    "required_commands": ["git status", "git add", "git commit"],
    "success_criteria": "Repository has at least one commit",
    "xp_reward": 50
  }},

  "git_state": {{
    "commits": [
      {{
        "id": "c1",
        "message": "Initial commit",
        "branch": "main",
        "parents": [],
        "timestamp": "2025-01-01"
      }}
    ],
    "branches": ["main"],
    "current_branch": "main"
  }},

  "word_count": 500
}}
```

**Important Guidelines:**
1. **Story First:** Every lesson starts with a Nexus Labs crisis/scenario
2. **No Passive Voice:** Active, conversational tone like a mentor teaching you
3. **Show, Don't Tell:** Use concrete examples, not abstract explanations
4. **Progressive Reveal:** Build complexity gradually through sections
5. **Git State:** Design a realistic Git repository state that matches the lesson
6. **Commands:** Only include commands actually taught in this lesson
7. **Challenge:** Must be doable with the commands learned
8. **Remove References:** NO mentions of DataCamp, videos, or original content creators

Return ONLY the JSON, no other text.
"""

    def generate_curriculum(self, tutorials_dir: str, output_dir: str):
        """
        Generate complete curriculum from all transcripts

        Args:
            tutorials_dir: Path to directory with transcript files
            output_dir: Path to save generated lessons
        """
        tutorials_path = Path(tutorials_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Load lesson mappings
        lesson_mappings = self._get_lesson_mappings()

        generated_lessons = []
        skipped_count = 0
        new_count = 0

        for level_dir in ['Introduction', 'Intermediate', 'Advanced']:
            level_path = tutorials_path / level_dir
            if not level_path.exists():
                continue

            print(f"\n{'='*60}")
            print(f"Processing {level_dir} Level")
            print(f"{'='*60}")

            for transcript_file in sorted(level_path.glob('*.txt')):
                lesson_id = transcript_file.stem

                # Get metadata
                metadata = lesson_mappings.get(lesson_id)
                if not metadata:
                    print(f"⚠ Skipping {lesson_id} - no mapping found")
                    continue

                # Check if lesson already exists
                output_file = output_path / f"{lesson_id}.json"
                if output_file.exists():
                    print(f"\n✓ Skipping {metadata['title']} - already generated")
                    print(f"   (Delete {output_file} to regenerate)")

                    # Load existing lesson for count
                    with open(output_file, 'r') as f:
                        existing_lesson = json.load(f)
                        generated_lessons.append(existing_lesson)
                    skipped_count += 1
                    continue

                print(f"\n📝 Generating: {metadata['title']}")
                print(f"   Level: {metadata['level']} | Order: {metadata['order_index']}")

                try:
                    # Generate lesson
                    lesson_data = self.generate_lesson(str(transcript_file), metadata)

                    # Add metadata
                    lesson_data['id'] = lesson_id
                    lesson_data['filename'] = transcript_file.name
                    lesson_data['title'] = metadata['title']
                    lesson_data['level'] = metadata['level']
                    lesson_data['order_index'] = metadata['order_index']

                    # Save to file
                    output_file = output_path / f"{lesson_id}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(lesson_data, f, indent=2, ensure_ascii=False)

                    print(f"   ✓ Generated {len(lesson_data['sections'])} sections")
                    print(f"   ✓ {len(lesson_data['git_commands'])} commands")
                    print(f"   ✓ Saved to {output_file}")

                    generated_lessons.append(lesson_data)
                    new_count += 1

                except Exception as e:
                    print(f"   ✗ Error: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

        print(f"\n{'='*60}")
        print(f"Curriculum Generation Complete!")
        print(f"{'='*60}")
        print(f"  Total lessons: {len(generated_lessons)}")
        print(f"  Newly generated: {new_count}")
        print(f"  Skipped (already exist): {skipped_count}")
        print(f"  Output directory: {output_path}")
        print(f"{'='*60}")

        return generated_lessons

    def _get_lesson_mappings(self) -> Dict:
        """Map transcript files to lesson metadata"""

        # Load from JSON file
        mappings_file = Path(__file__).parent.parent / "lesson_mappings.json"

        if mappings_file.exists():
            with open(mappings_file, 'r') as f:
                return json.load(f)

        # Fallback to empty dict
        return {}


if __name__ == "__main__":
    print("🎮 Git Quest - Curriculum Generator")
    print("=" * 60)

    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key.startswith('sk-ant-api03-your-key-here'):
        print("\n❌ ANTHROPIC_API_KEY not configured!")
        print("\nPlease add your API key to the .env file:")
        print("  1. Copy .env.example to .env")
        print("  2. Get your key from: https://console.anthropic.com/")
        print("  3. Add: ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key")
        print("\n")
        exit(1)

    print(f"✓ API key found: {api_key[:20]}...")
    print()

    generator = CurriculumGenerator()

    # Generate curriculum
    tutorials_dir = str(Path(__file__).parent.parent.parent)  # Root directory
    output_dir = str(Path(__file__).parent.parent / "generated_lessons")

    lessons = generator.generate_curriculum(tutorials_dir, output_dir)

    print(f"\n✨ Curriculum generation complete!")
    print(f"   Total lessons: {len(lessons)}")
    print(f"   Output directory: {output_dir}")
