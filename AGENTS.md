# Codex Project Guide

## Project

This repository is a portfolio project for a compact trading market dashboard.

Before implementing any task, read:

- `docs/spec.md`
- `docs/tasks/README.md`
- The requested task file under `docs/tasks/`
- The track-local `AGENTS.md` for the area you are editing:
  - `apps/backend/AGENTS.md` for backend work
  - `apps/frontend/AGENTS.md` for frontend work
  - `infra/AGENTS.md` for Docker, Kubernetes, and CI work
- Any task-specific spec referenced by the user

Track-local `AGENTS.md` files hold stack, coding standards, and verification rules for that area. This root file holds only cross-cutting rules.

## Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## Skill Usage

Use project-local skills for spec-first development.

Project-local skill paths:

- `.codex/skills/brainstorming`
- `.codex/skills/writing-plans`
- `.codex/skills/implement-task`
- `.codex/skills/requesting-code-review`

Standard flow:

```text
$brainstorming
$writing-plans backend TASK-01
$implement-task backend TASK-01
$requesting-code-review backend TASK-01
```

Use `$brainstorming` before changing project-level direction or designing a new feature.
Use `$writing-plans` before implementing or resizing a task.
Use `$implement-task` for normal task execution.
Use `$requesting-code-review` after implementation.

For this repository, Superpowers output locations are project-specific:

- Specs and project-level design should update `docs/spec.md` unless the user asks for a separate design document.
- Task plans should update the matching file under `docs/tasks/{track}/`.
- The task index should stay in `docs/tasks/README.md`.
- Do not create `docs/superpowers/` unless the user explicitly asks for Superpowers default output paths.

Before implementation:

- Check whether the user named a skill or whether an available skill clearly matches the task.
- If a skill applies, read its `SKILL.md` before editing files.
- State which skill is being used and why in a short working update.
- Follow the skill workflow for that task.
- If no available skill applies, continue with this project guide and mention that no task-specific skill was used.

When updating task notes, record:

- Skills used
- Important skill-specific decisions
- Any verification that the skill required

## Work With Worktrees

All work must run inside an isolated git worktree branched from `main`, then be merged back to `main`. The only exception is the very first bootstrap commit on `main`, since a worktree requires an existing ref.

Worktrees live under `.worktrees/` inside the repo root so VSCode (and any tool honoring `git.repositoryScanMaxDepth`) picks them up automatically. The `.worktrees/` directory itself is gitignored on `main`.

- Create a worktree per task: `git worktree add .worktrees/<task-id> -b <branch> main`
- Bind shared project config to the root copy so updates propagate to every live worktree without re-creating them:

  ```sh
  rm -rf .worktrees/<task-id>/.codex
  ln -s ../../.codex .worktrees/<task-id>/.codex
  ```

  Do this once per worktree right after `git worktree add`. The symlink resolves to the root `.codex/`, which always reflects `main`, so a merged skill or AGENTS update is visible inside every existing worktree immediately.
- Exception: if the task itself edits `.codex/` (a skill change, a Codex config change), skip the symlink step so the worktree keeps its own real copy on the feature branch.
- Do all editing, verification (lint/test/build), and commits inside the worktree.
- When two or more tasks have no shared state or sequential dependency, run them in parallel in separate worktrees. Do not edit the same files from multiple worktrees at the same time. If tasks share files or one depends on the other's output, do them sequentially.
- Merge the worktree branch into `main` only after verification passes inside that worktree.
- Remove the worktree after merge: `git worktree remove .worktrees/<task-id>`

## Scope Guardrails

- Keep the app scope small and production-shaped.
- Do not add login, signup, trading orders, payments, admin pages, or large unrelated features unless explicitly requested.
- Prefer completing one task at a time.
- Stay inside the task scope and acceptance criteria.
- Do not introduce a database in the MVP unless the task explicitly asks for it.
- Update docs when a task changes architecture, APIs, infrastructure, or development workflow.
