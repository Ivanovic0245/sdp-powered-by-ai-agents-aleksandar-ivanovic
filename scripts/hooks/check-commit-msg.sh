#!/bin/bash
# Enforces commit message format: #<issue> <type>(<scope>): <description>
# Example: #1 feat(auth): add login endpoint

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

PATTERN="^#[0-9]+ (feat|fix|chore|docs|style|refactor|test|ci|perf|build)\([a-zA-Z0-9_-]+\): .+"

if ! echo "$COMMIT_MSG" | grep -qE "$PATTERN"; then
  echo ""
  echo "ERROR: Invalid commit message format."
  echo ""
  echo "Expected: #<issue> <type>(<scope>): <description>"
  echo "Example:  #1 feat(auth): add login endpoint"
  echo ""
  echo "Types: feat, fix, chore, docs, style, refactor, test, ci, perf, build"
  echo ""
  exit 1
fi

exit 0
