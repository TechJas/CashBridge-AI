# CashBridge AI - Project Progress

Last updated: 2026-10-28  
Current phase: Phase 4 - Supabase schema and cash-flow foundation

## Phase 1 - Project initialization

- [x] Inspected the empty workspace and identified the read-only `references/AI-Toolkit` repository.
- [x] Created the initial project documentation: `README.md`, `AGENTS.md`, `.gitignore`, and `.env.example`.
- [x] Defined a modular monorepo layout for backend, frontend, Supabase, documentation, and scripts.
- [x] Documented security rules for PayPal Sandbox, secrets, human approval, and money calculations.
- [x] Initialized a dedicated Git repository on `main` instead of using the home-directory repository.
- [x] Published the initial commit to GitHub.

**Learning milestones**

- A monorepo keeps related applications together while separate folders keep responsibilities clear.
- Secrets belong in ignored local files, never in committed templates or source code.
- Human approval must be a backend rule, not only a frontend prompt.

## Phase 2 - Local environment and collaboration setup

- [x] Verified the Git working tree and connected `main` to the team GitHub repository.
- [x] Created a local Python virtual environment in the gitignored `.venv` folder.
- [x] Installed backend dependencies from `backend/requirements.txt`.
- [x] Confirmed that virtual environments, Python caches, and `.env` files are ignored by Git.
- [x] Established the workflow of small commits and pull requests to keep `main` runnable.

**Learning milestones**

- A virtual environment isolates project packages from the system Python installation.
- `git status` should be checked before every commit to catch files that should not be tracked.
- Dependencies belong in `requirements.txt`; generated environments and caches do not.

## Phase 3 - FastAPI backend and PayPal Sandbox

### Step 1 - Minimal FastAPI application

- [x] Created `backend/app/__init__.py` and `backend/app/main.py`.
- [x] Added `GET /health`, returning `{"status": "ok", "service": "cashbridge-api"}`.
- [x] Added the initial FastAPI and Uvicorn dependency ranges.
- [x] Verified the health endpoint through both FastAPI's test client and a running Uvicorn server.

### Step 2 - Configuration and repository state

- [x] Confirmed the backend files are tracked independently from the gitignored virtual environment.
- [x] Kept the existing health endpoint working while preparing for integration work.
- [x] Preserved the existing documentation and environment template structure.

### Step 3 - PayPal OAuth and invoice history

- [x] Added `app/core/config.py` for typed settings loaded from environment variables.
- [x] Added `python-dotenv` support for the gitignored `backend/.env`.
- [x] Added `app/integrations/paypal.py`, using `httpx` and the fixed PayPal Sandbox URL.
- [x] Implemented OAuth 2.0 client-credentials authentication.
- [x] Implemented `GET /api/invoices` using PayPal's `GET /v2/invoicing/invoices`.
- [x] Limited `page` to 1 or greater and `page_size` to 1-100.
- [x] Returned PayPal's JSON response, including its pagination fields.
- [x] Mapped missing credentials, authentication failures, network failures, timeouts, and upstream errors to safe HTTP responses.
- [x] Added `httpx` and `python-dotenv` to `backend/requirements.txt`.
- [x] Added the required PayPal variable placeholders to `.env.example`.
- [x] Created a local, gitignored `backend/.env` with blank placeholders for Sandbox credentials.

**Learning milestones**

- OAuth 2.0 client credentials exchange a client ID and secret for a short-lived access token.
- The access token is sent to PayPal in the `Authorization: Bearer ...` header and is never sent to the browser.
- Query validation with FastAPI prevents unsafe or excessively large invoice requests.
- External API failures should be translated into safe application errors without exposing response bodies or credentials.
- PayPal integration stays server-side and read-only; this step does not create invoices or move money.

### Step 4 - Service layer, response contract, and automated checks

- [x] Extracted PayPal orchestration into `app/services/invoice_service.py`; routes handle HTTP only.
- [x] Added `app/schemas/invoice.py` so `/api/invoices` exposes a typed `InvoiceListResponse` contract and OpenAPI schema.
- [x] Limited invoice responses to identifiers, dates, status, currency, and integer minor-unit totals; payer contact data is dropped.
- [x] Added deterministic money conversion in `app/core/money.py` using ISO 4217 minor-unit exponents and `Decimal`.
- [x] Added `FRONTEND_ORIGIN`-driven CORS and removed unused `PAYPAL_ENV`, `APP_*`, and `API_*` placeholders.
- [x] Added `backend/requirements-dev.txt`, Ruff and pytest configuration in `backend/pyproject.toml`, and a mocked PayPal test suite.
- [x] Added a transport injection point to `PayPalClient` so tests do not need network access.

**Learning milestones**

- A service layer keeps PayPal orchestration out of HTTP routes and makes the mapping testable.
- A response schema is also a security boundary: it decides which upstream fields reach the browser.
- Integer minor units plus `Decimal` avoid floating-point money errors.
- Mocked transports make failure-path tests fast and repeatable without Sandbox credentials.

## Verification performed

Run from `backend/`:

```text
..\.venv\Scripts\python.exe -m ruff check .
..\.venv\Scripts\python.exe -m ruff format --check .
..\.venv\Scripts\python.exe -m pytest
```

| Check | Result |
|---|---|
| `ruff check .` | Passed |
| `ruff format --check .` | Passed |
| `pytest` | 37 passed |
| `GET /health` | `200` with the expected JSON |
| `GET /api/invoices` without credentials | `503` with a safe configuration message |
| `page=0`, `page=-1`, `page_size=0`, `page_size=101` | `422` validation errors |
| OAuth token request and Bearer invoice request against a mocked transport | Passed |
| `page` and `page_size` forwarded to PayPal | Passed (`2` and `25`) |
| PayPal `401`/`403` responses | Mapped to a PayPal authentication error |
| PayPal timeout | Mapped to a `504` response |
| PayPal `500` response | Mapped to a safe `502` response |
| Invalid JSON and invalid amounts | Mapped to a safe `502` response |
| Credential leakage in error messages | None detected |
| Payer contact data in invoice responses | None; fields are dropped by the schema |
| OpenAPI schema contains `/api/invoices` and `InvoiceListResponse` | Passed |
| CORS preflight for the configured frontend origin | Passed |
| Live PayPal Sandbox request | Passed; 4 invoices returned and due dates mapped from `detail.payment_term.due_date` |

PayPal's list response returns `items` and `links` only for this Sandbox account, so `total_items` and `total_pages` may be `null`. Page size remains bounded by the validated `page` and `page_size` query parameters.

## Current security posture

- PayPal credentials are read only from backend environment variables.
- `backend/.env` is local and gitignored; `.env.example` contains placeholders only.
- The PayPal base URL is fixed to the Sandbox environment.
- No access tokens, client secrets, or raw PayPal error bodies are printed or returned.
- Invoice responses expose only a minimal set of fields; payer contact data is not forwarded.
- CORS allows only the configured `FRONTEND_ORIGIN`.
- The integration performs read-only invoice retrieval.
- Supabase, AI providers, authentication, and the React frontend are not connected yet.

## Phase 4 - Supabase schema and cash-flow foundation

### Step 1 - Core schema, RLS, and seed data

- [x] Decided on backend-only Supabase access with the service-role key; the browser will not call Supabase directly.
- [x] Decided on a single seeded demo business with `business_id` retained for future multi-tenancy.
- [x] Added `supabase/migrations/20261028000100_create_core_schema.sql`.
- [x] Added `businesses`, `customers`, `invoices`, `expenses`, `reminders`, `reminder_approvals`, and `reminder_send_attempts`.
- [x] Stored money as `bigint` integer minor units with ISO 4217 currency codes.
- [x] Added `updated_at` triggers for mutable tables.
- [x] Made approval and send-attempt records append-only with database triggers.
- [x] Added `supabase/migrations/20261028000200_enable_rls.sql`; RLS is enabled on every table and only the backend service role can access data.
- [x] Added entirely fictional seed data in `supabase/seed.sql` for one business, three customers, six invoices, five expenses, and two reminders.
- [ ] Apply both migrations and the seed to the team Supabase project through the SQL Editor.
- [ ] Add the backend repository layer and deterministic cash-flow service.

**Learning milestones**

- Backend-only Supabase access keeps the browser away from the database and the service-role key.
- Enabling RLS with no policies denies the anon and authenticated roles while the service role bypasses RLS.
- Append-only tables protect approval and send history from edits after the fact.
- Integer minor units plus ISO currency codes keep money exact across the database and API.

### How to apply (Supabase SQL Editor)

1. Open the project's SQL Editor.
2. Run `supabase/migrations/20261028000100_create_core_schema.sql`.
3. Run `supabase/migrations/20261028000200_enable_rls.sql`.
4. Run `supabase/seed.sql`.
5. Confirm with `select count(*) from public.businesses;` (expected `1`) and `select count(*) from public.invoices;` (expected `6`).

## Next steps

- Apply the Phase 4 migrations and seed data to the Supabase project.
- Add the backend Supabase client, repository layer, and deterministic cash-flow projections.
- Add the mock AI adapter for drafting reminder text (advisory only).
- Scaffold the React frontend and its API client using the generated OpenAPI contract.
- Add the human approval workflow before any reminder-sending feature is implemented.
