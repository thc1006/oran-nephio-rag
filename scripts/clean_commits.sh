#!/bin/bash

# This script removes Claude AI signatures from commit messages

git filter-branch -f --msg-filter '
sed -e "/🤖 Generated with \[Claude Code\]/d" \
    -e "/Co-Authored-By: Claude <noreply@anthropic.com>/d"
' HEAD~3..HEAD