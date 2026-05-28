---
name: implement-task
description: Implement one scoped project task from a spec or task index. Use when the user says `$implement-task`, asks to implement a track-scoped task such as `backend TASK-01`, `frontend TASK-02`, or `infra TASK-03`, or wants Codex to execute a defined task while staying inside acceptance criteria, running verification, and updating task status notes.
---

# Implement Task

## Overview

Use this skill to implement exactly one well-scoped task from a repository task board or spec. Keep the task bounded, verify the change, and record what was done.

## Workflow

1. Read the repository guidance first.
   - Prefer `AGENTS.md` when present.
   - Read project specs referenced by `AGENTS.md`.
   - Read the task board or task-specific spec named by the user.

2. Identify the requested task.
   - Prefer task files under `docs/tasks/`, for example `docs/tasks/backend/03-binance-candle-client.md`.
   - Use `docs/tasks/README.md` as the task index when present.
   - Find the exact track and task pair, such as `backend TASK-03`.
   - If the task cannot be found, search the repo for the task id.
   - If it still cannot be found, ask for the missing task details.

3. Restate the execution boundary before editing.
   - Goal
   - Scope
   - Out of scope
   - Acceptance criteria
   - Verification commands

4. Inspect the existing code before changing it.
   - Use fast search such as `rg` and targeted file reads.
   - Follow existing repo patterns.
   - Do not add unrelated architecture, features, dependencies, or refactors.

5. Implement the smallest complete change that satisfies the task.
   - Edit only files needed for the task.
   - Update documentation when API shape, setup, deployment, or workflow changes.
   - Preserve user changes and unrelated dirty worktree state.

6. Verify the task.
   - Run the task's listed verification commands.
   - If no commands are listed, choose focused checks based on the changed files.
   - If a check cannot run, record the reason.

7. Update the task file when one exists.
   - Mark the task status accurately.
   - Record files changed at a high level.
   - Record verification results.
   - Record `Skills used: implement-task`.

8. Finish with a concise report.
   - Say what changed.
   - Say what verification ran.
   - Mention any blocked or skipped checks.

## Scope Control

Do not broaden the task just because adjacent work is obvious.

Only add a dependency when the task requires it or the existing stack strongly implies it.

Do not implement future-work items unless the requested task explicitly includes them.

If the task is too broad, split it into smaller tasks in the task board instead of implementing everything at once.

## Task Update Format

When the repository does not already define a format, use this completion note:

```md
### Completion Notes

- Status: done
- Skills used: implement-task
- Changed: short summary of changed areas
- Verification: command and result, or reason not run
- Notes: important decisions or follow-up tasks
```

## Good User Prompts

```text
$implement-task backend TASK-01
```

```text
Use $implement-task to implement backend TASK-03 from docs/tasks/backend/03-binance-candle-client.md.
```

```text
$implement-task
Read AGENTS.md and docs/tasks/README.md.
Implement only infra TASK-03.
```
