#!/usr/bin/env bash
set -euo pipefail

# scripts/setup.sh
# Attempt to install `pre-commit` (prefer Homebrew), register hooks, and run formatting once.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Running repository setup from: $REPO_ROOT"
cd "$REPO_ROOT"

command_exists(){ command -v "$1" >/dev/null 2>&1; }

if command_exists pre-commit; then
  echo "pre-commit already installed: $(command -v pre-commit)"
else
  if command_exists brew; then
    echo "Installing pre-commit via Homebrew..."
    brew install pre-commit
  else
    if command_exists pipx || python3 -m pip --version >/dev/null 2>&1; then
      echo "Installing pre-commit via pipx..."
      if ! command_exists pipx; then
        python3 -m pip install --user pipx
        python3 -m pipx ensurepath || true
        echo "You may need to restart your shell for pipx binaries to be available."
      fi
      pipx install pre-commit
    else
      echo "No package manager found (brew/pipx). Trying pip as fallback..."
      python3 -m pip install --user pre-commit
    fi
  fi
fi

echo "Registering git hooks (pre-commit install)"
pre-commit install || { echo "pre-commit install failed"; exit 1; }

echo "Running pre-commit on all files (this will auto-format files)"
pre-commit run --all-files || echo "pre-commit run completed with non-zero status"

echo "Setup complete. If you use VS Code, ensure Prettier extension is set as default formatter and format on save (optional)."
echo "If you just installed pipx or changed PATH, you may need to restart your shell or terminal."

echo "Done."
