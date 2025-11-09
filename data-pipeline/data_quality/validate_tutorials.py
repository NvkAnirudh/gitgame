#!/usr/bin/env python3
"""
Git Quest Data Quality Validator
Validates parsed tutorial JSON files using Great Expectations principles
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of a validation check"""
    test_name: str
    passed: bool
    message: str
    severity: str = "error"  # "error", "warning", "info"


class DataQualityValidator:
    """Validates tutorial data quality"""

    # Valid Git commands (from parser)
    VALID_GIT_COMMANDS = {
        'git add', 'git add .', 'git commit', 'git status', 'git log', 'git show', 'git diff',
        'git branch', 'git checkout', 'git switch', 'git merge', 'git rebase', 'git reset', 'git revert',
        'git fetch', 'git pull', 'git push', 'git remote', 'git tag', 'git stash', 'git cherry-pick',
        'git reflog', 'git bisect', 'git submodule', 'git worktree', 'git filter-repo', 'git lfs',
        'git config', 'git help', 'git version', 'git restore', 'git clean', 'git rm', 'git mv',
        'git grep', 'git blame', 'git clone', 'git init'
    }

    # Valid levels
    VALID_LEVELS = {'introduction', 'intermediate', 'advanced'}

    def __init__(self):
        self.results: List[ValidationResult] = []
        self.tutorials_validated = 0
        self.errors = 0
        self.warnings = 0

    def validate_tutorial(self, filepath: Path) -> List[ValidationResult]:
        """Validate a single tutorial JSON file"""
        tutorial_results = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Test 1: Required fields exist
            tutorial_results.extend(self._test_required_fields(data, filepath.name))

            # Test 2: Field types are correct
            tutorial_results.extend(self._test_field_types(data, filepath.name))

            # Test 3: Level is valid
            tutorial_results.extend(self._test_valid_level(data, filepath.name))

            # Test 4: Sections are valid
            tutorial_results.extend(self._test_sections_structure(data, filepath.name))

            # Test 5: Section numbering is sequential
            tutorial_results.extend(self._test_sequential_sections(data, filepath.name))

            # Test 6: Timestamps are valid
            tutorial_results.extend(self._test_timestamps(data, filepath.name))

            # Test 7: Git commands are valid
            tutorial_results.extend(self._test_git_commands(data, filepath.name))

            # Test 8: Word count is reasonable
            tutorial_results.extend(self._test_word_count(data, filepath.name))

            # Test 9: Content completeness
            tutorial_results.extend(self._test_content_completeness(data, filepath.name))

            # Test 10: ID format is correct
            tutorial_results.extend(self._test_id_format(data, filepath.name))

            self.tutorials_validated += 1

        except json.JSONDecodeError as e:
            tutorial_results.append(ValidationResult(
                test_name="JSON Parsing",
                passed=False,
                message=f"{filepath.name}: Invalid JSON - {e}",
                severity="error"
            ))
        except Exception as e:
            tutorial_results.append(ValidationResult(
                test_name="General Validation",
                passed=False,
                message=f"{filepath.name}: Validation error - {e}",
                severity="error"
            ))

        # Count errors and warnings
        for result in tutorial_results:
            if not result.passed:
                if result.severity == "error":
                    self.errors += 1
                elif result.severity == "warning":
                    self.warnings += 1

        self.results.extend(tutorial_results)
        return tutorial_results

    def _test_required_fields(self, data: dict, filename: str) -> List[ValidationResult]:
        """Test that all required fields exist"""
        results = []
        required_fields = [
            'id', 'filename', 'level', 'title', 'sections',
            'total_sections', 'git_commands_used', 'learning_objectives',
            'word_count', 'parsed_at'
        ]

        for field in required_fields:
            if field not in data:
                results.append(ValidationResult(
                    test_name="Required Fields",
                    passed=False,
                    message=f"{filename}: Missing required field '{field}'",
                    severity="error"
                ))
            else:
                results.append(ValidationResult(
                    test_name="Required Fields",
                    passed=True,
                    message=f"{filename}: Field '{field}' exists",
                    severity="info"
                ))

        return results

    def _test_field_types(self, data: dict, filename: str) -> List[ValidationResult]:
        """Test that fields have correct types"""
        results = []

        type_checks = [
            ('id', str),
            ('filename', str),
            ('level', str),
            ('title', str),
            ('sections', list),
            ('total_sections', int),
            ('git_commands_used', list),
            ('learning_objectives', list),
            ('word_count', int),
            ('parsed_at', str)
        ]

        for field, expected_type in type_checks:
            if field in data:
                if isinstance(data[field], expected_type):
                    results.append(ValidationResult(
                        test_name="Field Types",
                        passed=True,
                        message=f"{filename}: '{field}' has correct type ({expected_type.__name__})",
                        severity="info"
                    ))
                else:
                    results.append(ValidationResult(
                        test_name="Field Types",
                        passed=False,
                        message=f"{filename}: '{field}' has wrong type (expected {expected_type.__name__}, got {type(data[field]).__name__})",
                        severity="error"
                    ))

        return results

    def _test_valid_level(self, data: dict, filename: str) -> List[ValidationResult]:
        """Test that level is valid"""
        results = []

        if 'level' in data:
            if data['level'] in self.VALID_LEVELS:
                results.append(ValidationResult(
                    test_name="Valid Level",
                    passed=True,
                    message=f"{filename}: Level '{data['level']}' is valid",
                    severity="info"
                ))
            else:
                results.append(ValidationResult(
                    test_name="Valid Level",
                    passed=False,
                    message=f"{filename}: Invalid level '{data['level']}' (must be one of {self.VALID_LEVELS})",
                    severity="error"
                ))

        return results

    def _test_sections_structure(self, data: dict, filename: str) -> List[ValidationResult]:
        """Test that sections have valid structure"""
        results = []

        if 'sections' in data and isinstance(data['sections'], list):
            required_section_fields = [
                'section_number', 'title', 'timestamp_start',
                'timestamp_end', 'content', 'git_commands'
            ]

            for i, section in enumerate(data['sections']):
                for field in required_section_fields:
                    if field not in section:
                        results.append(ValidationResult(
                            test_name="Section Structure",
                            passed=False,
                            message=f"{filename}: Section {i+1} missing field '{field}'",
                            severity="error"
                        ))

            if len(data['sections']) > 0:
                results.append(ValidationResult(
                    test_name="Section Structure",
                    passed=True,
                    message=f"{filename}: All sections have required fields",
                    severity="info"
                ))

        return results

    def _test_sequential_sections(self, data: dict, filename: str) -> List[ValidationResult]:
        """Test that section numbers are sequential"""
        results = []

        if 'sections' in data and isinstance(data['sections'], list):
            section_numbers = [s.get('section_number', -1) for s in data['sections']]

            # Check if sequential (1, 2, 3, ...)
            expected = list(range(1, len(data['sections']) + 1))
            if section_numbers == expected:
                results.append(ValidationResult(
                    test_name="Sequential Sections",
                    passed=True,
                    message=f"{filename}: Section numbers are sequential (1-{len(data['sections'])})",
                    severity="info"
                ))
            else:
                results.append(ValidationResult(
                    test_name="Sequential Sections",
                    passed=False,
                    message=f"{filename}: Section numbers are not sequential (expected {expected}, got {section_numbers})",
                    severity="warning"
                ))

        return results

    def _test_timestamps(self, data: dict, filename: str) -> List[ValidationResult]:
        """Test that timestamps are in valid format (HH:MM)"""
        results = []
        timestamp_pattern = re.compile(r'^\d{2}:\d{2}$')

        if 'sections' in data and isinstance(data['sections'], list):
            invalid_timestamps = []

            for section in data['sections']:
                start = section.get('timestamp_start', '')
                end = section.get('timestamp_end', '')

                if not timestamp_pattern.match(start):
                    invalid_timestamps.append(f"Section {section.get('section_number')}: start='{start}'")
                if not timestamp_pattern.match(end):
                    invalid_timestamps.append(f"Section {section.get('section_number')}: end='{end}'")

            if invalid_timestamps:
                results.append(ValidationResult(
                    test_name="Timestamp Format",
                    passed=False,
                    message=f"{filename}: Invalid timestamps - {', '.join(invalid_timestamps)}",
                    severity="warning"
                ))
            else:
                results.append(ValidationResult(
                    test_name="Timestamp Format",
                    passed=True,
                    message=f"{filename}: All timestamps are valid (HH:MM format)",
                    severity="info"
                ))

        return results

    def _test_git_commands(self, data: dict, filename: str) -> List[ValidationResult]:
        """Test that Git commands are valid"""
        results = []

        if 'git_commands_used' in data and isinstance(data['git_commands_used'], list):
            invalid_commands = []

            for cmd in data['git_commands_used']:
                if cmd not in self.VALID_GIT_COMMANDS:
                    invalid_commands.append(cmd)

            if invalid_commands:
                results.append(ValidationResult(
                    test_name="Valid Git Commands",
                    passed=False,
                    message=f"{filename}: Invalid/unknown Git commands - {invalid_commands}",
                    severity="warning"
                ))
            else:
                results.append(ValidationResult(
                    test_name="Valid Git Commands",
                    passed=True,
                    message=f"{filename}: All Git commands are valid ({len(data['git_commands_used'])} commands)",
                    severity="info"
                ))

        return results

    def _test_word_count(self, data: dict, filename: str) -> List[ValidationResult]:
        """Test that word count is reasonable"""
        results = []

        if 'word_count' in data:
            word_count = data['word_count']

            # Tutorials should have between 100 and 10,000 words
            if 100 <= word_count <= 10000:
                results.append(ValidationResult(
                    test_name="Word Count Range",
                    passed=True,
                    message=f"{filename}: Word count {word_count} is reasonable",
                    severity="info"
                ))
            elif word_count < 100:
                results.append(ValidationResult(
                    test_name="Word Count Range",
                    passed=False,
                    message=f"{filename}: Word count {word_count} is too low (minimum 100)",
                    severity="warning"
                ))
            else:
                results.append(ValidationResult(
                    test_name="Word Count Range",
                    passed=False,
                    message=f"{filename}: Word count {word_count} is suspiciously high (maximum 10,000)",
                    severity="warning"
                ))

        return results

    def _test_content_completeness(self, data: dict, filename: str) -> List[ValidationResult]:
        """Test that tutorial has meaningful content"""
        results = []

        # Check that there are sections
        if 'sections' in data and isinstance(data['sections'], list):
            section_count = len(data['sections'])

            if section_count >= 3:
                results.append(ValidationResult(
                    test_name="Content Completeness",
                    passed=True,
                    message=f"{filename}: Has {section_count} sections (good depth)",
                    severity="info"
                ))
            elif section_count > 0:
                results.append(ValidationResult(
                    test_name="Content Completeness",
                    passed=False,
                    message=f"{filename}: Only {section_count} sections (expected at least 3)",
                    severity="warning"
                ))
            else:
                results.append(ValidationResult(
                    test_name="Content Completeness",
                    passed=False,
                    message=f"{filename}: No sections found",
                    severity="error"
                ))

        # Check learning objectives exist
        if 'learning_objectives' in data and isinstance(data['learning_objectives'], list):
            if len(data['learning_objectives']) > 0:
                results.append(ValidationResult(
                    test_name="Learning Objectives",
                    passed=True,
                    message=f"{filename}: Has {len(data['learning_objectives'])} learning objectives",
                    severity="info"
                ))
            else:
                results.append(ValidationResult(
                    test_name="Learning Objectives",
                    passed=False,
                    message=f"{filename}: No learning objectives defined",
                    severity="warning"
                ))

        return results

    def _test_id_format(self, data: dict, filename: str) -> List[ValidationResult]:
        """Test that ID follows correct format (level-name)"""
        results = []

        if 'id' in data and 'level' in data:
            tutorial_id = data['id']
            level = data['level']

            # ID should start with level
            if tutorial_id.startswith(f"{level}-"):
                results.append(ValidationResult(
                    test_name="ID Format",
                    passed=True,
                    message=f"{filename}: ID '{tutorial_id}' follows correct format",
                    severity="info"
                ))
            else:
                results.append(ValidationResult(
                    test_name="ID Format",
                    passed=False,
                    message=f"{filename}: ID '{tutorial_id}' doesn't start with level '{level}-'",
                    severity="error"
                ))

        return results

    def validate_all(self, parsed_dir: str = 'content/parsed') -> Dict[str, Any]:
        """Validate all tutorial files"""
        parsed_path = Path(parsed_dir)

        if not parsed_path.exists():
            print(f"❌ Directory not found: {parsed_dir}")
            return {}

        # Get all JSON files except summary
        tutorial_files = [f for f in sorted(parsed_path.glob('*.json')) if f.name != 'summary.json']

        print(f"\n🔍 Git Quest Data Quality Validation")
        print("=" * 60)
        print(f"Validating {len(tutorial_files)} tutorials from {parsed_dir}/\n")

        # Validate each file
        for filepath in tutorial_files:
            print(f"📄 {filepath.name}...", end=' ')
            results = self.validate_tutorial(filepath)

            # Count passed/failed for this file
            errors = sum(1 for r in results if not r.passed and r.severity == "error")
            warnings = sum(1 for r in results if not r.passed and r.severity == "warning")

            if errors == 0 and warnings == 0:
                print("✅ PASS")
            elif errors == 0:
                print(f"⚠️  PASS with {warnings} warnings")
            else:
                print(f"❌ FAIL ({errors} errors, {warnings} warnings)")

        # Print summary
        self.print_summary()

        return self.generate_report()

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Tutorials Validated: {self.tutorials_validated}")
        print(f"Total Tests Run: {len(self.results)}")
        print(f"Passed: {sum(1 for r in self.results if r.passed)}")
        print(f"Errors: {self.errors}")
        print(f"Warnings: {self.warnings}")

        if self.errors == 0 and self.warnings == 0:
            print("\n✅ ALL VALIDATIONS PASSED!")
        elif self.errors == 0:
            print(f"\n⚠️  PASSED with {self.warnings} warnings")
        else:
            print(f"\n❌ FAILED with {self.errors} errors")

        # Print error details
        if self.errors > 0:
            print("\n🔴 ERRORS:")
            for result in self.results:
                if not result.passed and result.severity == "error":
                    print(f"  • {result.message}")

        # Print warning details (only first 10)
        if self.warnings > 0:
            print("\n🟡 WARNINGS (showing first 10):")
            warning_count = 0
            for result in self.results:
                if not result.passed and result.severity == "warning":
                    print(f"  • {result.message}")
                    warning_count += 1
                    if warning_count >= 10:
                        remaining = self.warnings - 10
                        if remaining > 0:
                            print(f"  ... and {remaining} more warnings")
                        break

        print("=" * 60)

    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'tutorials_validated': self.tutorials_validated,
            'total_tests': len(self.results),
            'passed': sum(1 for r in self.results if r.passed),
            'errors': self.errors,
            'warnings': self.warnings,
            'success': self.errors == 0,
            'results': [
                {
                    'test': r.test_name,
                    'passed': r.passed,
                    'message': r.message,
                    'severity': r.severity
                }
                for r in self.results
            ]
        }

    def save_report(self, output_file: str = 'data-pipeline/data_quality/validation_report.json'):
        """Save validation report to JSON file"""
        report = self.generate_report()

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"\n📝 Validation report saved to: {output_file}")


def main():
    """Main execution"""
    validator = DataQualityValidator()

    # Validate all tutorials
    validator.validate_all()

    # Save report
    validator.save_report()

    # Exit with error code if validation failed
    import sys
    sys.exit(0 if validator.errors == 0 else 1)


if __name__ == '__main__':
    main()
