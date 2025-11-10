"""
Git Sandbox Service - Safe Git command execution in isolated environments

This service creates isolated Git repositories for challenges, executes
commands safely, and validates results against success criteria.
"""

import os
import shutil
import tempfile
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import uuid
import git  # GitPython


# Git command whitelist for security
ALLOWED_GIT_COMMANDS = {
    'init', 'status', 'add', 'commit', 'log', 'diff', 'show',
    'branch', 'checkout', 'switch', 'merge', 'rebase', 'reset',
    'restore', 'revert', 'tag', 'stash', 'fetch', 'pull', 'push',
    'clone', 'remote', 'reflog', 'cherry-pick', 'bisect',
    'config', 'mv', 'rm', 'clean', 'blame', 'grep', 'describe',
    'worktree', 'submodule', 'ls-files', 'ls-tree', 'cat-file',
    'rev-parse', 'shortlog', 'whatchanged', 'for-each-ref'
}

# Shell command whitelist for lesson interaction
ALLOWED_SHELL_COMMANDS = {
    'pwd', 'ls', 'cd', 'cat', 'echo', 'mkdir', 'touch', 'rm',
    'cp', 'mv', 'find', 'tree', 'head', 'tail', 'wc', 'grep'
}

# Dangerous options to block
BLOCKED_OPTIONS = [
    '--exec', '--upload-pack', '--receive-pack', 'ext::', 'fd::',
    '|', ';', '&&', '||', '$', '`', '$(', '>'
]


class GitSandboxError(Exception):
    """Base exception for Git sandbox errors"""
    pass


class CommandNotAllowedError(GitSandboxError):
    """Raised when a dangerous command is attempted"""
    pass


class SandboxTimeoutError(GitSandboxError):
    """Raised when command execution times out"""
    pass


class GitSandbox:
    """
    Isolated Git repository sandbox for executing challenges

    Each sandbox is a temporary Git repository initialized with a specific
    git_state and isolated from the host system.
    """

    def __init__(self, sandbox_id: Optional[str] = None, base_dir: Optional[str] = None):
        """
        Initialize a Git sandbox

        Args:
            sandbox_id: Unique identifier for this sandbox (generated if None)
            base_dir: Base directory for sandboxes (uses temp if None)
        """
        self.sandbox_id = sandbox_id or str(uuid.uuid4())
        self.base_dir = base_dir or os.path.join(tempfile.gettempdir(), 'gitquest_sandboxes')
        self.repo_path = os.path.join(self.base_dir, self.sandbox_id)
        self.repo: Optional[git.Repo] = None
        self.created_at = datetime.utcnow()
        self.command_history: List[Dict[str, Any]] = []

        # Create base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)

    def initialize(self, git_state: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the sandbox Git repository

        Args:
            git_state: Git state to initialize (commits, branches, current_branch)
                      If None, creates an empty repository
        """
        if os.path.exists(self.repo_path):
            raise GitSandboxError(f"Sandbox {self.sandbox_id} already exists")

        # Create sandbox directory
        os.makedirs(self.repo_path, exist_ok=True)

        # Initialize Git repository
        self.repo = git.Repo.init(self.repo_path)

        # Configure Git user for commits
        with self.repo.config_writer() as git_config:
            git_config.set_value('user', 'email', 'player@gitquest.com')
            git_config.set_value('user', 'name', 'Git Quest Player')

        # Apply git_state if provided
        if git_state:
            self._apply_git_state(git_state)

    def _apply_git_state(self, git_state: Dict[str, Any]) -> None:
        """
        Apply a git_state to the repository

        Creates commits, branches, and sets HEAD according to the state

        Args:
            git_state: Dict with 'commits', 'branches', 'current_branch'
        """
        commits = git_state.get('commits', [])
        branches = git_state.get('branches', ['main'])
        current_branch = git_state.get('current_branch', 'main')

        # Create initial file structure
        readme_path = os.path.join(self.repo_path, 'README.md')

        # Process commits in order
        commit_map = {}  # Map commit IDs to actual commit objects

        for commit_data in commits:
            commit_id = commit_data.get('id')
            message = commit_data.get('message', 'Commit')
            branch_name = commit_data.get('branch', 'main')
            parents = commit_data.get('parents', [])
            files = commit_data.get('files', {})

            # Create or checkout branch
            if branch_name not in [b.name for b in self.repo.branches]:
                if self.repo.heads:
                    self.repo.create_head(branch_name)
                else:
                    # First commit - will create branch automatically
                    pass

            # Checkout branch if not already on it
            if self.repo.head.is_detached or self.repo.active_branch.name != branch_name:
                if branch_name in [b.name for b in self.repo.branches]:
                    self.repo.heads[branch_name].checkout()

            # Create/modify files for this commit
            if files:
                for file_path, content in files.items():
                    full_path = os.path.join(self.repo_path, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'w') as f:
                        f.write(content)
                    self.repo.index.add([file_path])
            else:
                # Default: modify README
                with open(readme_path, 'a') as f:
                    f.write(f"\n{message}\n")
                self.repo.index.add(['README.md'])

            # Create commit
            commit = self.repo.index.commit(message)
            commit_map[commit_id] = commit

        # Ensure all requested branches exist
        for branch in branches:
            if branch not in [b.name for b in self.repo.branches]:
                self.repo.create_head(branch)

        # Checkout the current branch
        if current_branch in [b.name for b in self.repo.branches]:
            self.repo.heads[current_branch].checkout()

    def execute_command(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """
        Execute a Git or shell command in the sandbox

        Args:
            command: Command to execute (e.g., "git status", "pwd", "ls")
            timeout: Maximum execution time in seconds

        Returns:
            Tuple of (success, stdout, stderr)

        Raises:
            CommandNotAllowedError: If command is not allowed
            SandboxTimeoutError: If command times out
        """
        # Validate command
        self._validate_command(command)

        # Record command
        start_time = datetime.utcnow()

        try:
            # Execute command in sandbox directory
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}  # Disable prompts
            )

            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr

        except subprocess.TimeoutExpired:
            raise SandboxTimeoutError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            success = False
            stdout = ""
            stderr = str(e)

        # Record in history
        end_time = datetime.utcnow()
        self.command_history.append({
            'command': command,
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'executed_at': start_time.isoformat(),
            'duration_ms': int((end_time - start_time).total_seconds() * 1000)
        })

        return success, stdout, stderr

    def _validate_command(self, command: str) -> None:
        """
        Validate that a command is safe to execute

        Args:
            command: Command to validate

        Raises:
            CommandNotAllowedError: If command is dangerous
        """
        # Check for blocked patterns
        for blocked in BLOCKED_OPTIONS:
            if blocked in command:
                raise CommandNotAllowedError(f"Command contains blocked pattern: {blocked}")

        # Parse command
        parts = command.strip().split()
        if not parts:
            raise CommandNotAllowedError("Empty command")

        base_command = parts[0]

        # Check if it's a git command
        if base_command == 'git':
            # Allow git with flags like 'git --version'
            if len(parts) > 1:
                next_part = parts[1]
                # If it starts with --, it's a flag (like --version, --help)
                if next_part.startswith('--'):
                    # Allow common git flags
                    allowed_flags = ['--version', '--help', '-h', '-v']
                    if next_part in allowed_flags:
                        return
                    # Otherwise check if it's a subcommand option
                    subcommand = next_part.lstrip('-').split('=')[0]
                    if subcommand in ALLOWED_GIT_COMMANDS:
                        return
                else:
                    # It's a subcommand
                    subcommand = next_part.lstrip('-').split('=')[0]
                    if subcommand not in ALLOWED_GIT_COMMANDS:
                        raise CommandNotAllowedError(f"Git subcommand not allowed: {subcommand}")
        # Check if it's an allowed shell command
        elif base_command in ALLOWED_SHELL_COMMANDS:
            return
        else:
            raise CommandNotAllowedError(f"Command not allowed: {base_command}")

    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current state of the Git repository

        Returns:
            Dictionary with current commits, branches, HEAD, status
        """
        if not self.repo:
            raise GitSandboxError("Sandbox not initialized")

        # Get branches
        branches = [branch.name for branch in self.repo.branches]

        # Get current branch or HEAD
        try:
            current_branch = self.repo.active_branch.name
            is_detached = False
        except TypeError:
            current_branch = str(self.repo.head.commit.hexsha[:7])
            is_detached = True

        # Get commits
        commits = []
        try:
            for commit in self.repo.iter_commits(max_count=50):
                commits.append({
                    'sha': commit.hexsha,
                    'short_sha': commit.hexsha[:7],
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'committed_date': commit.committed_datetime.isoformat(),
                    'parents': [p.hexsha[:7] for p in commit.parents]
                })
        except git.exc.GitCommandError:
            # No commits yet
            pass

        # Get status
        status = {
            'is_dirty': self.repo.is_dirty(),
            'untracked_files': self.repo.untracked_files,
            'changed_files': [item.a_path for item in self.repo.index.diff(None)],
            'staged_files': [item.a_path for item in self.repo.index.diff('HEAD')]
        }

        return {
            'branches': branches,
            'current_branch': current_branch,
            'is_detached': is_detached,
            'commits': commits,
            'status': status,
            'command_history': self.command_history
        }

    def validate_success_criteria(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the current repository state against success criteria

        Args:
            criteria: Success criteria from challenge

        Returns:
            Validation result with success, score, and details
        """
        required_commands = criteria.get('required_commands', [])
        description = criteria.get('description', '')

        criteria_met = []
        criteria_failed = []

        # Check required commands
        executed_commands = [cmd['command'] for cmd in self.command_history]
        for required_cmd in required_commands:
            if any(required_cmd in cmd for cmd in executed_commands):
                criteria_met.append(f"Executed required command: {required_cmd}")
            else:
                criteria_failed.append(f"Missing required command: {required_cmd}")

        # Check repository state (if specified)
        state = self.get_current_state()

        # Check for minimum commits
        min_commits = criteria.get('min_commits')
        if min_commits:
            commit_count = len(state['commits'])
            if commit_count >= min_commits:
                criteria_met.append(f"Has {commit_count} commits (required: {min_commits})")
            else:
                criteria_failed.append(f"Only {commit_count} commits (required: {min_commits})")

        # Check for specific branches
        required_branches = criteria.get('required_branches', [])
        for branch in required_branches:
            if branch in state['branches']:
                criteria_met.append(f"Branch exists: {branch}")
            else:
                criteria_failed.append(f"Missing branch: {branch}")

        # Check if working directory is clean
        if criteria.get('clean_working_directory', False):
            if not state['status']['is_dirty']:
                criteria_met.append("Working directory is clean")
            else:
                criteria_failed.append("Working directory has uncommitted changes")

        # Determine success
        success = len(criteria_failed) == 0

        return {
            'success': success,
            'criteria_met': criteria_met,
            'criteria_failed': criteria_failed,
            'total_criteria': len(criteria_met) + len(criteria_failed),
            'met_count': len(criteria_met),
            'description': description
        }

    def cleanup(self) -> None:
        """
        Clean up the sandbox (delete repository)
        """
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup sandbox"""
        self.cleanup()

    def __repr__(self):
        return f"GitSandbox(id={self.sandbox_id}, path={self.repo_path})"


class SandboxManager:
    """
    Manager for multiple Git sandboxes

    Handles sandbox creation, retrieval, and cleanup
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize sandbox manager

        Args:
            base_dir: Base directory for all sandboxes
        """
        self.base_dir = base_dir or os.path.join(tempfile.gettempdir(), 'gitquest_sandboxes')
        self.sandboxes: Dict[str, GitSandbox] = {}
        os.makedirs(self.base_dir, exist_ok=True)

    def create_sandbox(self, git_state: Optional[Dict[str, Any]] = None) -> GitSandbox:
        """
        Create a new sandbox

        Args:
            git_state: Initial git state for the sandbox

        Returns:
            Created GitSandbox instance
        """
        sandbox = GitSandbox(base_dir=self.base_dir)
        sandbox.initialize(git_state)
        self.sandboxes[sandbox.sandbox_id] = sandbox
        return sandbox

    def get_sandbox(self, sandbox_id: str) -> Optional[GitSandbox]:
        """
        Get an existing sandbox by ID

        Args:
            sandbox_id: Sandbox identifier

        Returns:
            GitSandbox instance or None if not found
        """
        return self.sandboxes.get(sandbox_id)

    def cleanup_sandbox(self, sandbox_id: str) -> bool:
        """
        Clean up a specific sandbox

        Args:
            sandbox_id: Sandbox to clean up

        Returns:
            True if cleaned up, False if not found
        """
        sandbox = self.sandboxes.pop(sandbox_id, None)
        if sandbox:
            sandbox.cleanup()
            return True
        return False

    def cleanup_all(self) -> int:
        """
        Clean up all sandboxes

        Returns:
            Number of sandboxes cleaned up
        """
        count = len(self.sandboxes)
        for sandbox in list(self.sandboxes.values()):
            sandbox.cleanup()
        self.sandboxes.clear()
        return count

    def cleanup_old_sandboxes(self, max_age_hours: int = 24) -> int:
        """
        Clean up sandboxes older than specified age

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of sandboxes cleaned up
        """
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        cleaned = 0

        for sandbox_id, sandbox in list(self.sandboxes.items()):
            if sandbox.created_at < cutoff:
                self.cleanup_sandbox(sandbox_id)
                cleaned += 1

        return cleaned


# Global sandbox manager instance
_sandbox_manager: Optional[SandboxManager] = None


def get_sandbox_manager() -> SandboxManager:
    """Get or create the global sandbox manager"""
    global _sandbox_manager
    if _sandbox_manager is None:
        _sandbox_manager = SandboxManager()
    return _sandbox_manager
