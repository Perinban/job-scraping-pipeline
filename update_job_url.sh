#!/bin/bash

# Set up Git configuration
git config --global user.name "GitHub Actions"
git config --global user.email "actions@github.com"

# Keep the current job URL snapshot without creating a new history entry every run.
if ! git diff --quiet job_post_url.txt; then
  git add job_post_url.txt
  git commit --amend --no-edit
  git push --force-with-lease origin HEAD:main || echo "Push failed, possibly due to conflicts or branch protection."
fi