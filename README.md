# CashBridge AI

CashBridge AI is an AI-assisted cash-flow copilot for small businesses. It helps owners see who owes them money, understand upcoming expenses, spot potential cash shortages, and prepare PayPal payment reminders that always require human approval.

> **Status:** Phase 1 - project initialization. The repository currently contains documentation and environment templates only. No application code or dependencies have been added yet.

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

CashBridge AI is a monorepo with four main areas:

```text
CashBridge-AI/
├── backend/    FastAPI application, business logic, and integrations
├── frontend/   React single-page application
├── supabase/   Database migrations, policies, and demo seed data
├── docs/       Setup guides, architecture notes, and decisions
└── scripts/    Small developer convenience scripts
```

Planned technology:

| Layer | Technology |
|---|---|
| Backend API | Python, FastAPI, Pydantic |
| Frontend | React, Vite, TypeScript |
| Database | Supabase Postgres with Row Level Security |
| Payments | PayPal Sandbox (server-side only) |
| AI | Provider adapter with a mock implementation first |
| Tooling | uv, Ruff, pytest, ESLint, TypeScript |

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
| `backend/` | FastAPI routes, schemas, services, repositories, and external integrations. |
| `frontend/` | React application organized by business feature. |
| `supabase/` | Versioned SQL migrations, Row Level Security policies, and seed data. |
| `docs/` | Setup instructions, architecture notes, API contract, and decision records. |
| `scripts/` | Safe helper scripts for local development. |
| `.github/` | Pull-request template and future CI checks. |
| `AGENTS.md` | Rules for AI coding assistants and the team. |

## Local development

Phase 1 does not install or run anything. The setup steps below are planned for Phase 2.

### Prerequisites

- Git
- Python and uv (versions will be pinned in Phase 2)
- Node.js and npm (versions will be pinned in Phase 2)
- A Supabase project
- PayPal Developer Sandbox credentials

### Planned setup

1. Copy `.env.example` values into `backend/.env`.
2. Create `frontend/.env.local` with the frontend values from `.env.example`.
3. Install backend dependencies with uv and frontend dependencies with npm.
4. Apply Supabase migrations.
5. Start the FastAPI and Vite development servers.

Exact commands and pinned versions will be documented in `docs/setup.md` once the application is scaffolded.

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
| 1 | Project initialization and repository guardrails (current) |
| 2 | Scaffold FastAPI and React applications |
| 3 | Design Supabase schema, policies, and seed data |
| 4 | Implement cash-flow logic, PayPal Sandbox integration, and AI adapter |
| 5 | Build the approval workflow, demo data, tests, and presentation |

## Documentation

Planned documents:

- `docs/setup.md` - local environment setup
- `docs/architecture.md` - system design and data flow
- `docs/api-contract.md` - endpoint and schema reference
- `docs/decisions/` - short architecture decision records

## License

To be decided by the team.
