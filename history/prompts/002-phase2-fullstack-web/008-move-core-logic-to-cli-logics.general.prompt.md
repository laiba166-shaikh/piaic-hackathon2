---
id: 008
title: Move Core Logic to cli/logics and Commit
stage: general
date: 2026-04-05
surface: agent
model: claude-sonnet-4-6
feature: 002-phase2-fullstack-web
branch: 002-phase2-fullstack-web
user: laiba166-shaikh
command: commit
labels: ["refactor","monorepo","cli","rename","git"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - src/cli/logics/__init__.py
  - src/cli/logics/models.py
  - src/cli/logics/exceptions.py
  - src/cli/logics/validators.py
  - src/cli/logics/recurring.py
  - src/cli/logics/services.py
  - src/cli/logics/storage/__init__.py
  - src/cli/logics/storage/base.py
  - src/cli/logics/storage/memory.py
  - src/cli/README.md
  - src/cli/pyproject.toml
  - src/cli/commands/basic.py
  - src/cli/commands/intermediate.py
  - src/cli/rendering/colors.py
  - src/cli/rendering/table.py
  - src/cli/tests/conftest.py
  - src/cli/tests/contract/test_storage_interface.py
  - src/cli/tests/unit/test_edge_cases.py
  - src/cli/tests/unit/test_models.py
  - src/cli/tests/unit/test_recurring.py
  - src/cli/tests/unit/test_search_filter.py
  - src/cli/tests/unit/test_services.py
  - src/cli/tests/unit/test_storage.py
  - src/cli/tests/unit/test_validators.py
  - src/cli/tests/validation/test_final_validation.py
  - specs/001-phase1-cli-todo/contracts/storage.py
  - "(deleted) src/core/models.py"
  - "(deleted) src/core/exceptions.py"
  - "(deleted) src/core/services.py"
  - "(deleted) src/core/validators.py"
  - "(deleted) src/core/recurring.py"
  - "(deleted) src/core/storage/"
tests:
  - none run
---

## Prompt

can you rename the folder name from cli to anyother appropriate
no change the core folder name under src/cli to logics
commit the changes

## Response snapshot

Renamed the `src/cli/core/` destination folder (which was being created as part of moving shared Phase 1 logic) to `src/cli/logics/`. Moved all shared files from `src/core/` (models, exceptions, validators, recurring, services, storage/) into `src/cli/logics/`, updated all imports from `src.core.` to `src.cli.logics.` across 15 consumer files, updated `pyproject.toml` packages list, deleted old `src/core/` shared files, and updated `src/cli/README.md` to reflect the new structure. Committed as `refactor(cli): move shared logic from src/core/ into src/cli/logics/` (commit `a31d238`).

## Outcome

- ✅ Impact: Phase 1 CLI is now fully self-contained under src/cli/; src/core/ only contains Phase 2 backend and frontend
- 🧪 Tests: Not run (refactor only — imports verified via smoke test)
- 📁 Files: 28 files changed; 9 new files in src/cli/logics/, 6 deleted from src/core/
- 🔁 Next prompts: Run pytest to verify all tests pass with new import paths
- 🧠 Reflection: Git correctly detected renames for exceptions.py, models.py, validators.py, storage/__init__.py, storage/memory.py

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): run pytest from src/cli/ to confirm all imports resolve correctly
