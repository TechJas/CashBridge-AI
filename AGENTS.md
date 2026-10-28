# AGENTS.md

This file defines how AI coding assistants and team members should work in the CashBridge AI repository. Read `README.md` first.

## Current state

The repository is in Phase 3. The FastAPI backend exposes a health check and a read-only PayPal Sandbox invoice-history endpoint with a Pydantic response contract, a service layer, and CORS. Dependencies are declared in `backend/requirements.txt`; test and lint dependencies are in `backend/requirements-dev.txt` and installed locally in the gitignored `.venv`. Ruff and pytest are configured in `backend/pyproject.toml`. Local credentials belong in the gitignored `backend/.env`. Supabase, AI providers, and the React frontend are not connected yet.

Do not assume a command, library, or configuration exists. Verify before using it, and update this file when the project setup changes.

## Non-negotiable safety rules

1. **Never commit secrets.** No API keys, tokens, passwords, webhook secrets, or real customer data in Git.
2. **Use PayPal Sandbox only.** Live PayPal endpoints and live credentials are out of scope.
3. **Never send a reminder without human approval.** The backend must require a stored approval record before contacting PayPal.
4. **Keep PayPal and Supabase service-role credentials server-side.** They must never reach the frontend bundle or browser network responses.
5. **Do not modify `references/AI-Toolkit`.** It is a read-only reference repository outside this project.
6. **Do not use floating-point arithmetic for money.** Store integer minor units and calculate with `Decimal` in the backend.
7. **Do not log secrets or unnecessary personal data.**
8. **Do not install dependencies, add integrations, or change the database schema without discussing it first.**
9. **Do not run destructive commands** such as deleting data, resetting Git history, or force-pushing.
10. **Do not commit changes unless a team member explicitly asks.**

## Architecture rules

Keep responsibilities separated:

- `api/` handles HTTP input and output only.
- `schemas/` defines Pydantic contracts. No database or business logic here.
- `services/` contains business rules and orchestration. No FastAPI request objects here.
- `db/repositories/` owns database access.
- `integrations/` owns PayPal, Supabase client setup, and AI provider calls.
- `frontend/src/api/` owns all HTTP calls from the browser.
- `frontend/src/features/` groups UI by feature rather than by file type.

A route should not contain SQL, PayPal calls, or forecasting logic. A service should not depend on HTTP details.

## Backend conventions

- Python with FastAPI and Pydantic.
- Use type hints on all public functions.
- Use async endpoints when they perform I/O.
- Validate every request with a Pydantic schema.
- Return consistent JSON errors with a safe message and an appropriate HTTP status.
- Keep configuration in `app/core/config.py`; read settings from environment variables, never hard-code secrets.
- Use UTC timestamps in ISO 8601 format.
- Use ISO dates for due dates and ISO 4217 currency codes for money.
- Use integer minor units for amounts in the database and API.
- Add unit tests for cash-flow and approval logic; add integration tests for API behavior.
- Use Ruff for formatting and linting.

## Frontend conventions

- React with Vite and TypeScript.
- Use functional components and explicit prop types.
- Keep components small and reusable.
- Put API calls in `src/api/`, not directly inside components.
- Show clear loading, empty, and error states.
- Never place secrets in frontend code or `VITE_` variables. Vite variables are public.
- Display money from integer minor units using a shared formatting helper.
- Use accessible labels, keyboard-friendly controls, and readable contrast.
- Run ESLint and the TypeScript checker before opening a pull request once configured.

## Database and Supabase conventions

- All schema changes go through versioned files in `supabase/migrations/`.
- Never edit a migration that has already been applied; add a new migration.
- Enable Row Level Security on every table containing business data.
- Include `business_id` on business-owned records to support future multi-tenancy.
- Restrict the service-role key to the backend. The frontend uses only the anon key.
- Keep seed data fictional and free of real personal information.
- Keep an immutable record of reminder approvals and send attempts.

## AI rules

- AI output is advisory and must be clearly presented as a suggestion.
- AI may draft reminder text and explain deterministic calculations.
- AI must not calculate totals, projections, or payment amounts.
- AI must not approve, send, or schedule payments.
- Put provider-specific code behind `integrations/ai.py`; start with a mock adapter.
- Send only the minimum necessary context to an AI provider. Never send secrets.
- Handle provider errors and timeouts gracefully; the app must still work without AI.

## Environment files

- `.env.example` is committed and contains placeholders only.
- Real values belong in `backend/.env` and `frontend/.env.local`; both are ignored by Git.
- Add new variables to `.env.example` in the same pull request that introduces them.
- Never print environment values in logs, screenshots, or issue comments.

## Git and pull requests

- Keep `main` runnable.
- Use short-lived branches: `feat/...`, `fix/...`, `docs/...`, or `chore/...`.
- Make small, focused commits with clear messages.
- Open a pull request for every change to `main`.
- At least one teammate must review a pull request before merge.
- In the pull request, state what changed, how it was tested, and any security impact.
- Do not commit generated build output, dependencies, coverage reports, or local environment files.

## Verification commands

```text
Backend setup (from the repository root):
  .venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt

Backend checks (from backend/):
  ..\.venv\Scripts\python.exe -m ruff check .
  ..\.venv\Scripts\python.exe -m ruff format --check .
  ..\.venv\Scripts\python.exe -m pytest

Backend server (from backend/):
  ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Health:   Invoke-RestMethod http://127.0.0.1:8000/health
Invoices: Invoke-RestMethod "http://127.0.0.1:8000/api/invoices?page=1&page_size=10"

Frontend (planned): npm run lint; npm run typecheck
```

The backend test suite mocks PayPal with `httpx.MockTransport`, so it does not require Sandbox credentials. A live Sandbox check still requires team-owned credentials in `backend/.env`.

## Definition of done

A change is complete when:

- The behavior is implemented and manually verified.
- Relevant tests pass.
- Linting and type checks pass.
- No secrets or real customer data are included.
- Documentation and `.env.example` are updated when needed.
- The change respects the human-approval and sandbox-only rules.
- A teammate has reviewed the pull request.

## Team ownership

| Area | Owner |
|---|---|
| Backend and API | Backend workstream |
| Frontend and UX | Frontend workstream |
| Data and Supabase | Data workstream |
| PayPal and AI integrations | Integration workstream |
| QA, documentation, DevOps | QA/DevOps workstream |

When ownership is unclear, discuss it in the pull request rather than making overlapping changes.
