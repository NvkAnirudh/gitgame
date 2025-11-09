#!/usr/bin/env python3
"""
Git Quest Tutorial Parser
Extracts structured data from tutorial transcript files (.txt)
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Section:
    """Represents a section in a tutorial"""
    section_number: int
    title: str
    timestamp_start: str
    timestamp_end: str
    content: str
    git_commands: List[str]


@dataclass
class Tutorial:
    """Represents a parsed tutorial"""
    id: str
    filename: str
    level: str  # 'introduction', 'intermediate', 'advanced'
    title: str
    sections: List[Section]
    total_sections: int
    git_commands_used: List[str]
    learning_objectives: List[str]
    practice_prompt: Optional[str]
    word_count: int
    parsed_at: str


class TutorialParser:
    """Parser for Git tutorial transcript files"""

    # Regex patterns
    SECTION_PATTERN = r'^(\d+)\.\s+(.+?)$'
    TIMESTAMP_PATTERN = r'^(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})$'

    # Git command vocabulary (base commands)
    GIT_COMMANDS = {
        'init', 'clone', 'add', 'commit', 'status', 'log', 'show', 'diff',
        'branch', 'checkout', 'switch', 'merge', 'rebase', 'reset', 'revert',
        'fetch', 'pull', 'push', 'remote', 'tag', 'stash', 'cherry-pick',
        'reflog', 'bisect', 'submodule', 'worktree', 'filter-repo', 'lfs',
        'config', 'help', 'version', 'restore', 'clean', 'rm', 'mv', 'grep',
        'blame', 'describe', 'shortlog', 'archive', 'bundle'
    }

    def __init__(self, tutorial_dirs: Dict[str, str]):
        """
        Initialize parser
        Args:
            tutorial_dirs: Dict mapping level names to directory paths
        """
        self.tutorial_dirs = tutorial_dirs
        self.parsed_tutorials = []

    def parse_file(self, filepath: Path, level: str) -> Optional[Tutorial]:
        """Parse a single tutorial file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                print(f"⚠️  Skipping empty file: {filepath.name}")
                return None

            lines = content.split('\n')
            sections = []
            current_section = None
            current_content = []

            for line in lines:
                line = line.rstrip()

                # Check if line is a section header
                section_match = re.match(self.SECTION_PATTERN, line)
                if section_match:
                    # Save previous section
                    if current_section:
                        sections.append(self._finalize_section(
                            current_section, current_content
                        ))

                    # Start new section
                    section_num = int(section_match.group(1))
                    section_title = section_match.group(2)
                    current_section = {
                        'section_number': section_num,
                        'title': section_title,
                        'timestamp_start': '',
                        'timestamp_end': '',
                    }
                    current_content = []
                    continue

                # Check if line is a timestamp
                timestamp_match = re.match(self.TIMESTAMP_PATTERN, line)
                if timestamp_match and current_section:
                    current_section['timestamp_start'] = timestamp_match.group(1)
                    current_section['timestamp_end'] = timestamp_match.group(2)
                    continue

                # Otherwise, it's content
                if current_section and line.strip():
                    current_content.append(line)

            # Save last section
            if current_section:
                sections.append(self._finalize_section(
                    current_section, current_content
                ))

            # Extract metadata
            tutorial_title = sections[0]['title'] if sections else filepath.stem
            all_git_commands = self._extract_all_git_commands(sections)
            learning_objectives = self._extract_learning_objectives(sections)
            practice_prompt = self._extract_practice_prompt(sections)

            # Create tutorial object
            tutorial = Tutorial(
                id=self._generate_id(filepath.stem, level),
                filename=filepath.name,
                level=level,
                title=tutorial_title,
                sections=[Section(**s) for s in sections],
                total_sections=len(sections),
                git_commands_used=all_git_commands,
                learning_objectives=learning_objectives,
                practice_prompt=practice_prompt,
                word_count=len(content.split()),
                parsed_at=datetime.now().isoformat()
            )

            return tutorial

        except Exception as e:
            print(f"❌ Error parsing {filepath.name}: {e}")
            return None

    def _finalize_section(self, section_data: dict, content_lines: List[str]) -> dict:
        """Finalize a section by extracting Git commands and combining content"""
        content = ' '.join(content_lines)
        git_commands = self._extract_git_commands(content)

        return {
            **section_data,
            'content': content,
            'git_commands': git_commands
        }

    def _extract_git_commands(self, text: str) -> List[str]:
        """Extract and normalize Git commands from text using LLM-style understanding"""
        commands = set()
        text_lower = text.lower()

        # Pattern 1: Direct command mentions (git <command>)
        for cmd in self.GIT_COMMANDS:
            # Look for "git <command>" patterns
            patterns = [
                rf'\bgit\s+{cmd}\b',
                rf'\bgit\s+{cmd}\s+\.',  # e.g., "git add ."
                rf'\bgit\s+{cmd}\s+-',   # e.g., "git commit -m"
                rf'\bgit\s+{cmd}\s+--',  # e.g., "git log --oneline"
            ]

            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # Normalize common variations
                    if 'git add .' in text_lower or 'git add dot' in text_lower:
                        commands.add('git add .')
                    elif cmd == 'add':
                        commands.add(f'git {cmd}')
                    else:
                        commands.add(f'git {cmd}')
                    break

        # Pattern 2: Common command phrases
        command_mappings = {
            'git add dot': 'git add .',
            'git add period': 'git add .',
            'git add all': 'git add .',
            'git commit -m': 'git commit',
            'git commit --amend': 'git commit',
            'git log --oneline': 'git log',
            'git log --all': 'git log',
            'git diff --staged': 'git diff',
            'git diff --cached': 'git diff',
            'git branch -d': 'git branch',
            'git branch -m': 'git branch',
            'git checkout -b': 'git checkout',
            'git merge --ff-only': 'git merge',
            'git merge --no-ff': 'git merge',
            'git merge --squash': 'git merge',
            'git rebase -i': 'git rebase',
            'git rebase --interactive': 'git rebase',
            'git reset --hard': 'git reset',
            'git reset --soft': 'git reset',
            'git push -u': 'git push',
            'git push --force': 'git push',
            'git pull origin': 'git pull',
            'git fetch origin': 'git fetch',
            'git remote add': 'git remote',
            'git remote -v': 'git remote',
            'git lfs track': 'git lfs',
            'git lfs install': 'git lfs',
            'git bisect start': 'git bisect',
            'git bisect good': 'git bisect',
            'git bisect bad': 'git bisect',
            'git worktree add': 'git worktree',
            'git worktree list': 'git worktree',
            'git submodule add': 'git submodule',
            'git submodule update': 'git submodule',
        }

        for phrase, normalized in command_mappings.items():
            if phrase in text_lower:
                commands.add(normalized)

        # Pattern 3: Context-based extraction (mentioned as doing something)
        # "we use git <command>", "run git <command>", "execute git <command>"
        context_patterns = [
            r'(?:use|using|run|running|execute|executing|type|typing)\s+git\s+(\w+)',
            r'git\s+(\w+)\s+command',
            r'the\s+git\s+(\w+)\s+command',
        ]

        for pattern in context_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match in self.GIT_COMMANDS:
                    commands.add(f'git {match}')

        return sorted(list(commands))

    def _extract_all_git_commands(self, sections: List[dict]) -> List[str]:
        """Extract all unique Git commands from all sections"""
        all_commands = []
        for section in sections:
            all_commands.extend(section.get('git_commands', []))
        return sorted(list(set(all_commands)))

    def _extract_learning_objectives(self, sections: List[dict]) -> List[str]:
        """Extract learning objectives (heuristic: commands and key concepts)"""
        # For now, use Git commands as learning objectives
        # Can be enhanced later with NLP
        objectives = []
        for section in sections:
            if 'git' in section.get('content', '').lower():
                objectives.append(section['title'])
        return objectives[:5]  # Top 5

    def _extract_practice_prompt(self, sections: List[dict]) -> Optional[str]:
        """Extract practice prompt if exists"""
        for section in sections:
            if 'practice' in section['title'].lower():
                return section.get('content', '')
        return None

    def _generate_id(self, filename: str, level: str) -> str:
        """Generate a unique ID for the tutorial"""
        # Format: level-filename
        clean_name = filename.replace('.txt', '').replace('_', '-').replace(' ', '-')
        return f"{level}-{clean_name}"

    def parse_all(self) -> List[Tutorial]:
        """Parse all tutorials in the specified directories"""
        all_tutorials = []

        for level, directory in self.tutorial_dirs.items():
            dir_path = Path(directory)
            if not dir_path.exists():
                print(f"⚠️  Directory not found: {directory}")
                continue

            print(f"\n📂 Parsing {level.upper()} tutorials from {directory}/")

            txt_files = sorted(dir_path.glob('*.txt'))
            for filepath in txt_files:
                print(f"  📄 {filepath.name}...", end=' ')
                tutorial = self.parse_file(filepath, level)
                if tutorial:
                    all_tutorials.append(tutorial)
                    print(f"✅ ({tutorial.total_sections} sections, {len(tutorial.git_commands_used)} commands)")
                else:
                    print("⏭️  Skipped")

        self.parsed_tutorials = all_tutorials
        return all_tutorials

    def save_to_json(self, output_dir: str = 'content/parsed'):
        """Save parsed tutorials to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\n💾 Saving parsed tutorials to {output_dir}/")

        for tutorial in self.parsed_tutorials:
            filename = f"{tutorial.id}.json"
            filepath = output_path / filename

            # Convert to dict
            tutorial_dict = asdict(tutorial)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tutorial_dict, f, indent=2, ensure_ascii=False)

            print(f"  ✅ {filename}")

        # Save summary file
        summary = self.generate_summary()
        summary_path = output_path / 'summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"  ✅ summary.json")

    def generate_summary(self) -> dict:
        """Generate summary statistics"""
        total_tutorials = len(self.parsed_tutorials)
        total_sections = sum(t.total_sections for t in self.parsed_tutorials)

        # Count by level
        level_counts = {}
        for tutorial in self.parsed_tutorials:
            level_counts[tutorial.level] = level_counts.get(tutorial.level, 0) + 1

        # Collect all Git commands
        all_commands = set()
        for tutorial in self.parsed_tutorials:
            all_commands.update(tutorial.git_commands_used)

        return {
            'total_tutorials': total_tutorials,
            'total_sections': total_sections,
            'tutorials_by_level': level_counts,
            'total_git_commands': len(all_commands),
            'git_commands': sorted(list(all_commands)),
            'parsed_at': datetime.now().isoformat()
        }

    def print_summary(self):
        """Print summary statistics"""
        summary = self.generate_summary()

        print("\n" + "="*60)
        print("📊 PARSING SUMMARY")
        print("="*60)
        print(f"Total Tutorials Parsed: {summary['total_tutorials']}")
        print(f"Total Sections: {summary['total_sections']}")
        print(f"\nBy Level:")
        for level, count in summary['tutorials_by_level'].items():
            print(f"  • {level.capitalize()}: {count} tutorials")
        print(f"\nTotal Git Commands Found: {summary['total_git_commands']}")
        print(f"\nGit Commands:")
        for cmd in summary['git_commands'][:10]:  # Show first 10
            print(f"  • {cmd}")
        if len(summary['git_commands']) > 10:
            print(f"  ... and {len(summary['git_commands']) - 10} more")
        print("="*60)


def main():
    """Main execution"""
    print("🚀 Git Quest Tutorial Parser")
    print("="*60)

    # Define tutorial directories
    tutorial_dirs = {
        'introduction': 'Introduction',
        'intermediate': 'Intermediate',
        'advanced': 'Advanced'
    }

    # Parse tutorials
    parser = TutorialParser(tutorial_dirs)
    tutorials = parser.parse_all()

    # Save to JSON
    parser.save_to_json()

    # Print summary
    parser.print_summary()

    print(f"\n✅ Parsing complete! {len(tutorials)} tutorials processed.")


if __name__ == '__main__':
    main()
