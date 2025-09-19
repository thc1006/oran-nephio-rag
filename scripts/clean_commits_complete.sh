#!/bin/bash

# Clean the last 3 commits by removing Claude signatures completely
git filter-branch -f --msg-filter '
grep -v "🤖 Generated with \[Claude Code\]" | grep -v "Co-Authored-By: Claude"
' HEAD~3..HEAD