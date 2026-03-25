# Plan: Fix Workflow Skipping After PR Merge

## Overview

The GitHub Actions workflow (`.github/workflows/mainworkflow.yml`) is designed to fire after a PR is merged and create three GitHub Issues (UI/UX, Backend, Testing) assigned to the Copilot coding agent. However, the workflow is **always skipped** when a Copilot-created PR is merged, due to two bugs in the workflow logic:

1. **Branch filter blocks Copilot PRs** – The job `if` condition contains `!startsWith(github.head_ref || '', 'copilot/')`, which unconditionally skips any PR from a branch whose name starts with `copilot/`. Since the planning agent always creates branches like `copilot/plan-*`, the workflow never runs after the plan PR is merged.

2. **Wrong file path for the plan** – The workflow checks for `planning.md` at the repository root, but the actual planning document lives at `planned/plan.md`. Even if bug #1 were fixed, the step "Create agent issues" would still be skipped because `planning.md` never exists at the root.

**Additional improvement**: Issue bodies currently contain only a generic static string. They should embed the actual content of `planned/plan.md` so the Copilot agents have all the context they need to implement the feature.

---

## Root Cause Analysis

| # | Root Cause | Location | Effect |
|---|---|---|---|
| 1 | `!startsWith(github.head_ref \|\| '', 'copilot/')` | `mainworkflow.yml` job `if` condition (line 28) | Job is skipped for all Copilot-created planning PRs |
| 2 | Checks for `planning.md` at repo root | `mainworkflow.yml` step "Check for planning.md" (line 47) | Issue creation step is skipped; file is actually at `planned/plan.md` |
| 3 | Issue bodies are static generic strings | `mainworkflow.yml` issue definition block (lines 101–114) | Copilot agents lack the plan context needed to implement the feature |

---

## Desired Workflow Behaviour (After Fix)

```
PR merged into main/default branch
        │
        ▼
Does the PR modify `planned/plan.md`?
        │
   Yes  │  No ──► Skip (no new plan to act on)
        │
        ▼
Read content of `planned/plan.md`
        │
        ▼
Create three GitHub Issues (UI/UX, Backend, Testing)
  • Each issue body includes the full plan content
  • Each issue is labelled `copilot` and assigned to the Copilot agent
  • Duplicate open issues with the same title are skipped
```

To avoid infinite loops (Copilot implementation PRs triggering more issues), the workflow will only fire when `planned/plan.md` is modified in the merged PR. Implementation PRs (UI/UX, backend, testing) will never touch `planned/plan.md`, so they will be naturally filtered out without needing actor- or branch-based exclusions.

---

## Task List

### 1. Fix Job-Level `if` Condition

**File:** `.github/workflows/mainworkflow.yml`

- [ ] **1.1** Remove the `!startsWith(github.head_ref || '', 'copilot/')` line from the job `if` condition. This line was added to prevent infinite loops but it also blocks the planning-agent PR from triggering issue creation.
- [ ] **1.2** Remove the `github.actor != 'copilot[bot]'` and `github.actor != 'github-actions[bot]'` exclusions. These are no longer needed once we use path-based filtering (step 2 below) to distinguish planning PRs from implementation PRs.
- [ ] **1.3** Remove the `!contains(github.event.pull_request.labels.*.name, 'skip-uiux-automation')` label-based exclusion. Replace this with path-based filtering so the logic is explicit and self-documenting.
- [ ] **1.4** The simplified job `if` condition should become:

  ```yaml
  if: >
    github.event.pull_request.merged == true ||
    github.event_name == 'workflow_dispatch'
  ```

  > **Loop-safety note:** Loop prevention is now handled entirely by path filtering in step 1.5 — only PRs that touch `planned/plan.md` will proceed to create issues. Implementation agent PRs (UI/UX, backend, testing) never modify `planned/plan.md`, so no issues will be created for them.

- [ ] **1.5** Add a new step immediately after the checkout step to detect whether `planned/plan.md` was changed in the merged PR. Use `git diff` against the base SHA to identify modified files:

  ```yaml
  - name: Check if planned/plan.md was modified
    id: check-plan-changed
    run: |
      BASE_SHA="${{ github.event.pull_request.base.sha }}"
      HEAD_SHA="${{ github.event.pull_request.head.sha }}"
      if [ -n "$BASE_SHA" ] && [ -n "$HEAD_SHA" ]; then
        CHANGED=$(git diff --name-only "$BASE_SHA" "$HEAD_SHA" 2>/dev/null || echo "")
      else
        # workflow_dispatch: treat as changed so manual trigger always works
        CHANGED="planned/plan.md"
      fi
      if echo "$CHANGED" | grep -q "^planned/plan.md$"; then
        echo "changed=true" >> "$GITHUB_OUTPUT"
      else
        echo "changed=false" >> "$GITHUB_OUTPUT"
        echo "::notice::planned/plan.md was not modified in this PR — skipping issue creation."
      fi
  ```

---

### 2. Fix the `planned/plan.md` Path Check

**File:** `.github/workflows/mainworkflow.yml`

- [ ] **2.1** Update the "Check for planning.md" step to look for `planned/plan.md` instead of `planning.md`:

  ```yaml
  - name: Check for planned/plan.md
    id: check-planning
    if: steps.check-plan-changed.outputs.changed == 'true'
    run: |
      if [ -f "planned/plan.md" ]; then
        echo "exists=true" >> "$GITHUB_OUTPUT"
      else
        echo "exists=false" >> "$GITHUB_OUTPUT"
        echo "::warning::planned/plan.md not found on branch ${{ github.event.pull_request.base.ref || github.ref_name }}. Skipping issue creation."
      fi
  ```

- [ ] **2.2** Update the `if` condition on the "Create agent issues" step to also guard on `check-plan-changed`:

  ```yaml
  if: steps.check-plan-changed.outputs.changed == 'true' && steps.check-planning.outputs.exists == 'true'
  ```

---

### 3. Embed `planned/plan.md` Content in Issue Bodies

**File:** `.github/workflows/mainworkflow.yml`

- [ ] **3.1** Add a step before the issue-creation step to read `planned/plan.md` into an output variable:

  ```yaml
  - name: Read plan content
    id: read-plan
    if: steps.check-plan-changed.outputs.changed == 'true' && steps.check-planning.outputs.exists == 'true'
    run: |
      PLAN_CONTENT=$(cat planned/plan.md)
      # Use GitHub's multiline output syntax
      {
        echo "content<<EOF_PLAN"
        echo "$PLAN_CONTENT"
        echo "EOF_PLAN"
      } >> "$GITHUB_OUTPUT"
  ```

- [ ] **3.2** Update the issue definitions in the `actions/github-script` step to include the plan content in each issue body. Pass the plan content via an environment variable to avoid quoting issues:

  ```yaml
  env:
    PLAN_CONTENT: ${{ steps.read-plan.outputs.content }}
  ```

  Issue body template for each agent type:

  ```
  ## Task: <Agent Type> Changes

  Implement the <agent type> changes described in `planned/plan.md`.

  ---

  ## Plan Content

  <plan content injected here>

  ---

  > This issue was automatically created by the CI workflow after merging the planning PR.
  > Implement only the <agent type> section of the plan above.
  ```

- [ ] **3.3** Update the three issue definitions in the script:

  ```javascript
  const planContent = process.env.PLAN_CONTENT || '_(plan content unavailable)_';

  const issues = [
    {
      title: 'UI/UX changes',
      body: `## Task: UI/UX Changes\n\nImplement the UI/UX changes described in \`planned/plan.md\`.\n\n---\n\n## Plan Content\n\n${planContent}\n\n---\n\n> This issue was automatically created by the CI workflow after merging the planning PR.\n> Implement only the UI/UX section of the plan above.`,
    },
    {
      title: 'Backend changes',
      body: `## Task: Backend Changes\n\nImplement the backend service changes described in \`planned/plan.md\`.\n\n---\n\n## Plan Content\n\n${planContent}\n\n---\n\n> This issue was automatically created by the CI workflow after merging the planning PR.\n> Implement only the backend section of the plan above.`,
    },
    {
      title: 'Testing changes',
      body: `## Task: Testing Changes\n\nImplement the testing framework changes described in \`planned/plan.md\`.\n\n---\n\n## Plan Content\n\n${planContent}\n\n---\n\n> This issue was automatically created by the CI workflow after merging the planning PR.\n> Implement only the testing section of the plan above.`,
    },
  ];
  ```

---

### 4. Complete Updated Workflow File

**File:** `.github/workflows/mainworkflow.yml`

Replace the entire file with the following (this is the canonical target state after all fixes):

```yaml
name: Create multiple issues

# Trigger: fires when a PR is merged (and planned/plan.md was modified),
# or manually via workflow_dispatch.
# Reads planned/plan.md and creates three GitHub Issues (UI/UX, Backend, Testing)
# assigned to the Copilot coding agent.
on:
  pull_request:
    types: [closed]
    paths:
      - 'planned/plan.md'
  workflow_dispatch:

# Prevent duplicate runs for the same PR
concurrency:
  group: trigger-agents-${{ github.event.pull_request.number || 'manual' }}
  cancel-in-progress: false

jobs:
  create-agent-issues:
    # Only run when the PR was actually merged (not just closed),
    # OR this is a manual dispatch.
    if: >
      github.event.pull_request.merged == true ||
      github.event_name == 'workflow_dispatch'

    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: read

    steps:
      # Check out the target branch (after merge) so we can read planned/plan.md
      - name: Checkout target branch
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.base.ref || github.ref_name }}
          fetch-depth: 0

      # Check whether planned/plan.md exists
      - name: Check for planned/plan.md
        id: check-planning
        run: |
          if [ -f "planned/plan.md" ]; then
            echo "exists=true" >> "$GITHUB_OUTPUT"
          else
            echo "exists=false" >> "$GITHUB_OUTPUT"
            echo "::warning::planned/plan.md not found on branch ${{ github.event.pull_request.base.ref || github.ref_name }}. Skipping issue creation."
          fi

      # Read plan content into an output variable
      - name: Read plan content
        id: read-plan
        if: steps.check-planning.outputs.exists == 'true'
        run: |
          {
            echo "content<<EOF_PLAN"
            cat planned/plan.md
            echo "EOF_PLAN"
          } >> "$GITHUB_OUTPUT"

      # Create three issues: UI/UX, Backend, and Testing
      - name: Create agent issues from planned/plan.md
        if: steps.check-planning.outputs.exists == 'true'
        uses: actions/github-script@v7
        env:
          PLAN_CONTENT: ${{ steps.read-plan.outputs.content }}
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            // --- Ensure the 'copilot' label exists ---
            try {
              await github.rest.issues.getLabel({
                owner: context.repo.owner,
                repo:  context.repo.repo,
                name:  'copilot',
              });
            } catch {
              await github.rest.issues.createLabel({
                owner: context.repo.owner,
                repo:  context.repo.repo,
                name:  'copilot',
                color: '1d76db',
              });
              core.info('Created missing label: "copilot"');
            }

            // --- Check if copilot can be assigned ---
            let canAssignCopilot = false;
            try {
              await github.rest.issues.checkUserCanBeAssigned({
                owner:    context.repo.owner,
                repo:     context.repo.repo,
                assignee: 'copilot',
              });
              canAssignCopilot = true;
            } catch {
              core.warning('Assignee "copilot" is not valid for this repository — skipping assignment.');
            }

            // --- Fetch existing open copilot issues for dedup ---
            const { data: existingIssues } = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo:  context.repo.repo,
              state: 'open',
              labels: 'copilot',
              per_page: 100,
            });

            const planContent = process.env.PLAN_CONTENT || '_(plan content unavailable)_';

            // --- Define the three issues ---
            const issues = [
              {
                title: 'UI/UX changes',
                body: `## Task: UI/UX Changes\n\nImplement the UI/UX changes described in \`planned/plan.md\`.\n\n---\n\n## Plan Content\n\n${planContent}\n\n---\n\n> This issue was automatically created by the CI workflow after merging the planning PR.\n> Implement only the UI/UX section of the plan above.`,
              },
              {
                title: 'Backend changes',
                body: `## Task: Backend Changes\n\nImplement the backend service changes described in \`planned/plan.md\`.\n\n---\n\n## Plan Content\n\n${planContent}\n\n---\n\n> This issue was automatically created by the CI workflow after merging the planning PR.\n> Implement only the backend section of the plan above.`,
              },
              {
                title: 'Testing changes',
                body: `## Task: Testing Changes\n\nImplement the testing framework changes described in \`planned/plan.md\`.\n\n---\n\n## Plan Content\n\n${planContent}\n\n---\n\n> This issue was automatically created by the CI workflow after merging the planning PR.\n> Implement only the testing section of the plan above.`,
              },
            ];

            // --- Create each issue (skip duplicates) ---
            for (const issue of issues) {
              const duplicate = existingIssues.find(i => i.title === issue.title);
              if (duplicate) {
                core.info(`Open issue already exists: #${duplicate.number} "${issue.title}" — skipping.`);
                continue;
              }

              const createParams = {
                owner:  context.repo.owner,
                repo:   context.repo.repo,
                title:  issue.title,
                body:   issue.body,
                labels: ['copilot'],
              };

              if (canAssignCopilot) {
                createParams.assignees = ['copilot'];
              }

              const { data: created } = await github.rest.issues.create(createParams);
              core.info(`Created issue #${created.number}: ${created.html_url}`);
            }
```

> **Key changes from original:**
> - `paths: ['planned/plan.md']` on the `pull_request` trigger — only runs when the plan file changed (loop prevention)
> - `fetch-depth: 0` on checkout — needed to compare SHAs
> - Job renamed `create-agent-issues` for clarity
> - Simplified `if` — no more actor/branch exclusions
> - File path changed from `planning.md` → `planned/plan.md`
> - Issue bodies include full plan content via `$PLAN_CONTENT` env variable

---

### 5. Validation / Testing

- [ ] **5.1** After applying the workflow changes, merge a PR that modifies `planned/plan.md` and verify:
  - The "Create multiple issues" workflow run is **not skipped**.
  - Three issues are created: "UI/UX changes", "Backend changes", "Testing changes".
  - Each issue body contains the full content of `planned/plan.md`.
  - Issues are labelled `copilot` and assigned to the Copilot agent.

- [ ] **5.2** Merge a PR that does **not** modify `planned/plan.md` (e.g., a backend implementation PR) and verify:
  - The workflow does **not** run (filtered by the `paths` trigger).

- [ ] **5.3** Trigger the workflow manually via `workflow_dispatch` and verify:
  - All three issues are created successfully.
  - Issue bodies contain the current `planned/plan.md` content.

- [ ] **5.4** Verify duplicate detection: if the three issues already exist in open state with the `copilot` label, re-running the workflow should log "skipping" for each and not create duplicate issues.

---

### 6. Definition of Done

- [ ] Workflow `mainworkflow.yml` no longer has the `!startsWith(github.head_ref || '', 'copilot/')` exclusion.
- [ ] Workflow file path for the plan document is `planned/plan.md` (not `planning.md`).
- [ ] The `paths` trigger filter on the workflow prevents it from running on implementation-only PRs, eliminating infinite-loop risk.
- [ ] All three issues (UI/UX, Backend, Testing) are created when a planning PR is merged.
- [ ] Each issue body includes the full `planned/plan.md` content so agents have complete context.
- [ ] No duplicate issues are created on re-runs.
