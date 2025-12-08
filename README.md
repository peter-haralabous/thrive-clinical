# Static Site

This repository has been wiped and replaced with a minimal static site to be hosted with GitHub Pages.

To publish to GitHub Pages (from `main` branch):

1. Commit and push to the `main` branch.
2. In the repository settings -> Pages, set the source to the `main` branch root.

That's it — your `index.html` will be served at `https://<your-username>.github.io/<repo>/`.

## Local setup (pre-commit + Prettier)

This repository includes a minimal `.pre-commit-config.yaml` and `.prettierrc` to auto-format files on commit.

If you prefer Homebrew (recommended on macOS), run the project setup script which will install `pre-commit`, register the hooks, and run formatters once:

```bash
# from the repo root
scripts/setup.sh
```

Alternatively run the commands manually:

```bash
# Install pre-commit using Homebrew (or pipx/pip if you prefer)
brew install pre-commit

# Then in the repo root
pre-commit install
pre-commit run --all-files
```

If you use VS Code, enable the Prettier extension and set `editor.formatOnSave` for instant local formatting (optional).

# Static Site

This repository has been wiped and replaced with a minimal static site to be hosted with GitHub Pages.

To publish to GitHub Pages (from `main` branch):

1. Commit and push to the `main` branch.
2. In the repository settings -> Pages, set the source to the `main` branch root.

That's it — your `index.html` will be served at `https://<your-username>.github.io/<repo>/`.
