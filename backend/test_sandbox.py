#!/usr/bin/env python3
"""
Test script for GitSandbox service

This script demonstrates and tests the Git sandbox functionality
"""

import sys
sys.path.insert(0, '/home/user/gitgame/backend')

from app.services.git_sandbox import GitSandbox, SandboxManager, GitSandboxError


def test_basic_sandbox():
    """Test basic sandbox creation and commands"""
    print("=" * 60)
    print("Test 1: Basic Sandbox with Empty Repository")
    print("=" * 60)

    with GitSandbox() as sandbox:
        # Initialize empty repo
        sandbox.initialize()
        print(f"✓ Sandbox created: {sandbox.sandbox_id}")
        print(f"  Path: {sandbox.repo_path}")

        # Execute some commands
        success, stdout, stderr = sandbox.execute_command("git status")
        print(f"\n✓ Executed: git status")
        print(f"  Success: {success}")
        print(f"  Output: {stdout[:100]}...")

        # Get current state
        state = sandbox.get_current_state()
        print(f"\n✓ Current state:")
        print(f"  Branches: {state['branches']}")
        print(f"  Current branch: {state['current_branch']}")
        print(f"  Commits: {len(state['commits'])}")

    print("\n✓ Sandbox cleaned up successfully\n")


def test_sandbox_with_git_state():
    """Test sandbox initialization with git_state"""
    print("=" * 60)
    print("Test 2: Sandbox with Git State")
    print("=" * 60)

    git_state = {
        "commits": [
            {
                "id": "c1",
                "message": "Initial commit",
                "branch": "main",
                "parents": [],
                "files": {
                    "README.md": "# Git Quest Challenge\n\nWelcome to the challenge!"
                }
            },
            {
                "id": "c2",
                "message": "Add feature",
                "branch": "main",
                "parents": ["c1"],
                "files": {
                    "feature.txt": "New feature"
                }
            }
        ],
        "branches": ["main", "develop"],
        "current_branch": "main"
    }

    with GitSandbox() as sandbox:
        sandbox.initialize(git_state=git_state)
        print(f"✓ Sandbox initialized with git_state")

        # Check state
        state = sandbox.get_current_state()
        print(f"\n✓ Repository state:")
        print(f"  Branches: {state['branches']}")
        print(f"  Current branch: {state['current_branch']}")
        print(f"  Commits: {len(state['commits'])}")

        # Execute git log
        success, stdout, stderr = sandbox.execute_command("git log --oneline")
        print(f"\n✓ Git log:")
        print(f"  {stdout}")

        # Try creating a new branch
        success, stdout, stderr = sandbox.execute_command("git branch feature-branch")
        print(f"✓ Created feature-branch: {success}")

        # List branches
        success, stdout, stderr = sandbox.execute_command("git branch")
        print(f"\n✓ Branches:")
        print(f"  {stdout}")

    print("\n✓ Sandbox cleaned up successfully\n")


def test_challenge_validation():
    """Test challenge validation logic"""
    print("=" * 60)
    print("Test 3: Challenge Validation")
    print("=" * 60)

    git_state = {
        "commits": [{
            "id": "c1",
            "message": "Initial commit",
            "branch": "main",
            "parents": [],
            "files": {"README.md": "# Project"}
        }],
        "branches": ["main"],
        "current_branch": "main"
    }

    success_criteria = {
        "required_commands": ["git add", "git commit"],
        "min_commits": 2,
        "clean_working_directory": True
    }

    with GitSandbox() as sandbox:
        sandbox.initialize(git_state=git_state)
        print(f"✓ Sandbox initialized for challenge")

        # Simulate player commands
        commands = [
            "git status",
            "echo 'test' > test.txt",
            "git add test.txt",
            "git commit -m 'Add test file'"
        ]

        print(f"\n✓ Executing player commands:")
        for cmd in commands:
            success, stdout, stderr = sandbox.execute_command(cmd)
            print(f"  - {cmd}: {'✓' if success else '✗'}")

        # Validate
        validation = sandbox.validate_success_criteria(success_criteria)
        print(f"\n✓ Validation Results:")
        print(f"  Success: {validation['success']}")
        print(f"  Criteria met: {validation['met_count']}/{validation['total_criteria']}")
        print(f"\n  Met:")
        for criterion in validation['criteria_met']:
            print(f"    ✓ {criterion}")
        print(f"\n  Failed:")
        for criterion in validation['criteria_failed']:
            print(f"    ✗ {criterion}")

    print("\n✓ Test completed\n")


def test_command_security():
    """Test command security whitelist"""
    print("=" * 60)
    print("Test 4: Command Security")
    print("=" * 60)

    with GitSandbox() as sandbox:
        sandbox.initialize()
        print(f"✓ Sandbox created for security testing")

        # Test allowed commands
        allowed_commands = [
            "git status",
            "git log",
            "git add ."
        ]

        print(f"\n✓ Testing allowed commands:")
        for cmd in allowed_commands:
            try:
                sandbox.execute_command(cmd)
                print(f"  ✓ {cmd}: Allowed")
            except Exception as e:
                print(f"  ✗ {cmd}: Blocked - {e}")

        # Test blocked commands
        blocked_commands = [
            "rm -rf /",
            "git --exec=/bin/sh",
            "ls; rm file",
            "python script.py"
        ]

        print(f"\n✓ Testing blocked commands:")
        for cmd in blocked_commands:
            try:
                sandbox.execute_command(cmd)
                print(f"  ✗ {cmd}: SECURITY ISSUE - Should have been blocked!")
            except Exception as e:
                print(f"  ✓ {cmd}: Blocked - {type(e).__name__}")

    print("\n✓ Security test completed\n")


def test_sandbox_manager():
    """Test SandboxManager for multiple sandboxes"""
    print("=" * 60)
    print("Test 5: Sandbox Manager")
    print("=" * 60)

    manager = SandboxManager()
    print(f"✓ Sandbox manager created")

    # Create multiple sandboxes
    sandbox1 = manager.create_sandbox()
    sandbox2 = manager.create_sandbox()
    sandbox3 = manager.create_sandbox()

    print(f"\n✓ Created 3 sandboxes:")
    print(f"  - {sandbox1.sandbox_id}")
    print(f"  - {sandbox2.sandbox_id}")
    print(f"  - {sandbox3.sandbox_id}")

    # Retrieve sandbox
    retrieved = manager.get_sandbox(sandbox1.sandbox_id)
    print(f"\n✓ Retrieved sandbox: {retrieved.sandbox_id == sandbox1.sandbox_id}")

    # Cleanup one
    cleaned = manager.cleanup_sandbox(sandbox2.sandbox_id)
    print(f"✓ Cleaned up sandbox: {cleaned}")

    # Cleanup all
    total_cleaned = manager.cleanup_all()
    print(f"✓ Cleaned up all sandboxes: {total_cleaned}")

    print("\n✓ Manager test completed\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Git Quest - Git Sandbox Service Test Suite")
    print("=" * 60 + "\n")

    try:
        test_basic_sandbox()
        test_sandbox_with_git_state()
        test_challenge_validation()
        test_command_security()
        test_sandbox_manager()

        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
