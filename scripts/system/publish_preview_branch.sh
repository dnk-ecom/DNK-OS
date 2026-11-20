#!/bin/bash
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/publish_preview_branch.sh"
# purpose: "Zero-friction publisher for dnk-preview orphan branch and Cloudflare Pages sync."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PREVIEW_SRC="$REPO_ROOT/docs/projects/dnk_ecom/distillations"
BRANCH="dnk-preview"
PROJECT_NAME="dnk-preview"

echo "🧬 [DNK OS] Starting Safe Preview Synchronization..."

if [ ! -d "$PREVIEW_SRC" ]; then
  echo "❌ Error: Distillations directory not found at $PREVIEW_SRC"
  exit 1
fi

TEMP_WT="/tmp/dnk_preview_wt_$$"
cleanup() {
  if [ -d "$TEMP_WT" ]; then
    echo "🧹 Cleaning up temporary worktree: $TEMP_WT"
    git -C "$REPO_ROOT" worktree remove --force "$TEMP_WT" 2>/dev/null || rm -rf "$TEMP_WT"
  fi
}
trap cleanup EXIT

echo "📦 Preparing isolated git worktree for branch '$BRANCH'..."

# Check if branch exists locally or on remote
BRANCH_EXISTS=0
if git -C "$REPO_ROOT" rev-parse --verify --quiet "refs/heads/$BRANCH" >/dev/null 2>&1; then
  BRANCH_EXISTS=1
elif git -C "$REPO_ROOT" rev-parse --verify --quiet "refs/remotes/origin/$BRANCH" >/dev/null 2>&1; then
  BRANCH_EXISTS=1
fi

if [ $BRANCH_EXISTS -eq 1 ]; then
  echo "🌿 Checking out existing branch '$BRANCH' into isolated worktree..."
  git -C "$REPO_ROOT" worktree add "$TEMP_WT" "$BRANCH"
else
  echo "🌱 Creating new isolated orphan branch '$BRANCH'..."
  git -C "$REPO_ROOT" worktree add --orphan -b "$BRANCH" "$TEMP_WT"
fi

# Clean worktree files (except .git)
echo "📂 Synchronizing static preview assets..."
find "$TEMP_WT" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

# Copy all distillations to root of worktree
cp -R "$PREVIEW_SRC"/* "$TEMP_WT"/

# Stage and commit
cd "$TEMP_WT"
git add -A

if git diff-index --quiet HEAD -- 2>/dev/null; then
  echo "ℹ️  No changes detected in preview assets. Git tree is up to date."
else
  COMMIT_MSG="chore(preview): sync design systems and showcases ($(date -u +'%Y-%m-%d %H:%M:%S UTC')) [skip ci]"
  git commit --no-verify -m "$COMMIT_MSG"
  echo "🚀 Pushing branch '$BRANCH' to origin..."
  git push origin "$BRANCH"
  echo "✅ Successfully pushed '$BRANCH' to GitHub!"
fi

cd "$REPO_ROOT"

# Deploy to Cloudflare Pages via Wrangler for instant edge CDN propagation
echo "⛅ Deploying to Cloudflare Pages edge CDN ($PROJECT_NAME)..."
pnpm dlx wrangler pages deploy "$PREVIEW_SRC" --project-name="$PROJECT_NAME" --branch="$BRANCH"

echo ""
echo "=========================================================="
echo "🎉 [DNK OS] Preview Deployment Complete!"
echo "🌐 Hub Portal:       https://$PROJECT_NAME.pages.dev/"
echo "🛍️  Sugar Theme:     https://$PROJECT_NAME.pages.dev/sugar_theme/index.html"
echo "🏡  Pergolux:        https://$PROJECT_NAME.pages.dev/pergolux/index.html"
echo "🌿 GitHub Branch:    https://github.com/dnk-ecom/DNK-OS/tree/$BRANCH"
echo "=========================================================="
