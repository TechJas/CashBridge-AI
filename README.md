# CashBridge AI

CashBridge AI is an AI-assisted cash-flow copilot for small businesses. It helps owners see who owes them money, understand upcoming expenses, spot potential cash shortages, and prepare PayPal payment reminders that always require human approval.

> **Status:** Phase 3 - PayPal Sandbox invoice history. The FastAPI backend exposes `/health` and a read-only `/api/invoices` endpoint with Pydantic response contracts, a service layer, CORS, and automated pytest and Ruff checks. Supabase, AI providers, and the React frontend are not connected yet.

## The problem

Small businesses often track invoices in spreadsheets and expenses in several different places. This makes it hard to answer three simple questions:

1. Which invoices are unpaid or overdue?
2. What bills are coming up in the next 30, 60, or 90 days?
3. Will there be enough cash to cover them?

CashBridge AI brings this information into one place, highlights cash-flow risks, and helps draft polite payment reminders. A person must review and approve every reminder before it is sent.

## MVP scope

- Track customers, invoices, due dates, and payment status.
- Track upcoming and recurring expenses.
- Project cash flow over the next 30, 60, and 90 days.
- Flag potential cash shortages and overdue invoices.
- Use AI to explain risks in plain language and draft reminder messages.
- Place reminders in a human approval queue.
- Send approved reminders through the PayPal Sandbox.
- Keep an audit trail of approvals and sending attempts.

## Non-goals for the hackathon

- No live PayPal payments or live customer data.
- No automatic sending without explicit human approval.
- No AI-generated financial calculations. Money math stays deterministic.
- No browser access to PayPal secrets or Supabase service-role credentials.
- No production deployment or long-term data retention.

## Architecture

CashBridge AI is a monorepo. Folders marked planned are part of the target layout but do not contain application code yet:

```text
CashBridge-AI/
├── backend/    FastAPI application, business logic, and integrations (implemented)
├── frontend/   React single-page application (planned)
├── supabase/   Database migrations, policies, and demo seed data (planned)
├── docs/       Progress notes, setup guides, and decisions (implemented)
└── scripts/    Small developer convenience scripts (planned)
```

Technology:

| Layer | Technology |
|---|---|
| Backend API | Python, FastAPI, Pydantic |
| Frontend | React, Vite, TypeScript |
| Database | Supabase Postgres with Row Level Security |
| Payments | PayPal Sandbox (server-side only) |
| AI | Provider adapter with a mock implementation first |
| Tooling (backend) | Ruff, pytest |
| Tooling (frontend, planned) | ESLint, TypeScript |

### How a reminder is handled

```text
AI drafts message
      |
      v
draft -> pending_approval -> approved -> sent
                                  |
                                  +-----> failed
```

The backend must refuse to send a reminder unless an approval record exists. The browser never talks to PayPal directly.

### Money handling

All monetary values are stored and transferred as integer minor units (for example, cents) together with an ISO 4217 currency code. Backend calculations use `Decimal`. Floating-point numbers are never used for money.

## Repository layout

| Path | Purpose |
|---|---|
| `backend/` | FastAPI routes, schemas, services, and external integrations (implemented). |
| `frontend/` | React application organized by business feature (planned). |
| `supabase/` | Versioned SQL migrations, Row Level Security policies, and seed data (planned). |
| `docs/` | Progress notes, setup instructions, architecture notes, and decisions. |
| `scripts/` | Safe helper scripts for local development (planned). |
| `.github/` | Pull-request template and CI checks (planned). |
| `AGENTS.md` | Rules for AI coding assistants and the team. |

## Local development

### Prerequisites

- Git
- Python 3.11 or newer
- PayPal Developer Sandbox credentials

React and Supabase prerequisites will be added when those parts are scaffolded.

### Backend setup

1. Copy `.env.example` values into `backend/.env` and fill in the PayPal Sandbox credentials.
2. Create a virtual environment at the repository root: `python -m venv .venv`.
3. Install backend and developer dependencies: `.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt`.
4. Start the API from `backend`: `..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.

### Verification commands

Run these from `backend`:

```text
..\.venv\Scripts\python.exe -m ruff check .
..\.venv\Scripts\python.exe -m ruff format --check .
..\.venv\Scripts\python.exe -m pytest
```

The test suite mocks PayPal with `httpx.MockTransport`, so it needs no Sandbox credentials.

## Security and safety rules

- Never commit `.env` files, API keys, tokens, or customer data.
- `.env.example` contains variable names and safe placeholders only.
- Use PayPal Sandbox only. Live payments are out of scope.
- PayPal and Supabase service-role credentials stay on the backend.
- Enable Row Level Security on every business table.
- Require a recorded human approval before sending any reminder.
- Keep AI advisory: it may draft and explain, but it cannot approve or move money.
- Do not log secrets or unnecessary personal data.
- Treat `references/AI-Toolkit` as read-only reference material.

## Team workstreams

| Workstream | Primary areas |
|---|---|
| Backend and API | `backend/app/api`, `backend/app/core` |
| Frontend and UX | `frontend/src/features`, `frontend/src/components` |
| Data and Supabase | `supabase/`, `backend/app/db` |
| PayPal and AI integrations | `backend/app/integrations`, `backend/app/services` |
| QA, documentation, DevOps | `backend/tests`, `docs/`, `.github/`, `scripts/` |

### Collaboration workflow

- `main` stays runnable and protected.
- Use short-lived branches such as `feat/invoice-list` or `fix/reminder-status`.
- Require at least one review before merging.
- Update documentation and `.env.example` in the same pull request as configuration changes.
- Keep pull requests focused on one feature or fix.

## Roadmap

| Phase | Goal |
|---|---|
| 1 | Project initialization and repository guardrails |
| 2 | Local environment and collaboration setup |
| 3 | FastAPI backend and PayPal Sandbox invoice history (current) |
| 4 | Supabase schema, cash-flow logic, and AI adapter |
| 5 | Approval workflow, React frontend, demo data, and presentation |

## Documentation

- `docs/PROJECT_PROGRESS.md` - completed work, verification results, and next steps
- `docs/setup.md` - local environment setup (planned)
- `docs/architecture.md` - system design and data flow (planned)
- `docs/api-contract.md` - endpoint and schema reference (planned)
- `docs/decisions/` - short architecture decision records (planned)

## License

To be decided by the team.
