#!/usr/bin/env python3
"""Script to remove Claude AI signatures from git commits."""

import subprocess
import sys

def get_commit_message(commit_hash):
    """Get the full commit message."""
    result = subprocess.run(
        ['git', 'log', '--format=%B', '-n', '1', commit_hash],
        capture_output=True, text=True
    )
    return result.stdout

def clean_message(message):
    """Remove Claude AI signatures from message."""
    lines = message.split('\n')
    cleaned_lines = []

    for line in lines:
        # Skip lines with Claude signatures
        if '🤖 Generated with [Claude Code]' in line:
            continue
        if 'Co-Authored-By: Claude' in line:
            continue
        cleaned_lines.append(line)

    # Remove trailing empty lines
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()

    return '\n'.join(cleaned_lines)

def main():
    # Get the last 3 commits
    commits = ['HEAD~2', 'HEAD~1', 'HEAD']

    print("Cleaning commit messages...")

    for i, commit in enumerate(commits):
        # Get commit hash
        result = subprocess.run(
            ['git', 'rev-parse', commit],
            capture_output=True, text=True
        )
        commit_hash = result.stdout.strip()

        # Get and clean message
        message = get_commit_message(commit_hash)
        cleaned = clean_message(message)

        print(f"\nCommit {i+1} ({commit_hash[:8]}):")
        print("=" * 50)
        print(cleaned)
        print("=" * 50)

    print("\nTo apply these changes, you'll need to use interactive rebase.")
    print("Run: git rebase -i HEAD~3")
    print("Then change 'pick' to 'reword' for each commit")

if __name__ == "__main__":
    main()