# agenticworkflow_GHCP

Authentication flow scaffold with a FastAPI backend and FastUI frontend.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── models/
│   │   ├── services/
│   │   └── core/
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── app/
│   ├── pyproject.toml
│   └── README.md
└── README.md
```

## Quick Start

Start the backend in one terminal:

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e .
uvicorn app.main:app --reload --port 8000
```

Start the frontend in another terminal:

```bash
cd frontend
uv venv
source .venv/bin/activate
uv pip install -e .
export BACKEND_URL="http://localhost:8000"
uvicorn app.main:app --reload --port 8001
```

Visit `http://localhost:8001` to use the login UI.

---

## Automated UI/UX Agent Pipeline

This repository uses a GitHub Actions workflow to **automatically trigger the UI/UX coding agent** whenever a PR is merged into `Planning_Branch`.

### How it works

```
Developer merges a PR into Planning_Branch
        │
        ▼
GitHub Actions: "Trigger UI/UX Agent on PR Merge"
  1. Checks out Planning_Branch
  2. Reads planning.md from the repository root
  3. Extracts the "## UI/UX" section
  4. Creates a GitHub Issue titled "[UI/UX] Implement changes from planning.md"
     • Labels: ui/ux, copilot
     • Assignee: copilot (the Copilot coding agent)
        │
        ▼
GitHub Copilot coding agent picks up the issue
  • Reads planning.md as the source of truth
  • Makes frontend-only code changes
  • Opens a new Pull Request automatically
```

### Required setup

| Setting | Value |
|---------|-------|
| Workflow permissions | **Read and write** (Settings → Actions → General → Workflow permissions) |
| Token | `GITHUB_TOKEN` (built-in, no PAT needed) |
| GitHub Copilot | Must be enabled and the `copilot` assignee must be valid for the repo |

To enable **Read and write** permissions:
1. Go to **Settings → Actions → General** in the repository.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Save.

### planning.md format

For reliable extraction, include a `## UI/UX Changes` (or `## UI/UX`) section:

```markdown
## UI/UX Changes

- [ ] Update login form styling
- [ ] Add loading spinner on form submit
- [ ] Show inline error messages

### Acceptance Criteria
- All interactive states (loading, error, success) are visible
```

If no `## UI/UX` section is found, the entire `planning.md` is passed to the agent.

### Loop prevention (idempotency)

The workflow will **not** re-trigger when:

| Guard | Mechanism |
|-------|-----------|
| PR opened by the Copilot agent | `github.actor != 'copilot[bot]'` |
| PR opened by GitHub Actions | `github.actor != 'github-actions[bot]'` |
| Head branch starts with `copilot/` | `!startsWith(github.head_ref, 'copilot/')` |
| PR has the opt-out label | `!contains(labels, 'skip-uiux-automation')` |

### Controlling the automation

| Goal | Action |
|------|--------|
| Skip the automation for a specific PR | Add the label **`skip-uiux-automation`** to the PR before merging |
| Disable permanently | Remove or comment-out `.github/workflows/create-uiux-issue.yml` |
| Trigger manually (e.g. for testing) | Go to **Actions → Trigger UI/UX Agent on PR Merge → Run workflow** |

### Workflow file

`.github/workflows/create-uiux-issue.yml`
