create extension if not exists pgcrypto;

create table public.businesses (
    id uuid primary key default gen_random_uuid(),
    name text not null check (length(trim(name)) > 0),
    base_currency text not null default 'USD'
        check (base_currency ~ '^[A-Z]{3}$'),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table public.customers (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null
        references public.businesses (id) on delete cascade,
    name text not null check (length(trim(name)) > 0),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index customers_business_id_idx on public.customers (business_id);

create table public.invoices (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null
        references public.businesses (id) on delete cascade,
    customer_id uuid
        references public.customers (id) on delete set null,
    paypal_invoice_id text not null,
    invoice_number text,
    status text not null default 'DRAFT' check (
        status in (
            'DRAFT',
            'SENT',
            'SCHEDULED',
            'PAID',
            'MARKED_AS_PAID',
            'PARTIALLY_PAID',
            'PARTIALLY_REFUNDED',
            'REFUNDED',
            'CANCELLED'
        )
    ),
    invoice_date date not null,
    due_date date,
    currency_code text not null check (currency_code ~ '^[A-Z]{3}$'),
    total_minor_units bigint not null default 0
        check (total_minor_units >= 0),
    amount_due_minor_units bigint not null default 0
        check (amount_due_minor_units >= 0),
    synced_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (business_id, paypal_invoice_id)
);

create index invoices_business_due_date_idx
    on public.invoices (business_id, due_date);
create index invoices_business_status_idx
    on public.invoices (business_id, status);

create table public.expenses (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null
        references public.businesses (id) on delete cascade,
    vendor text not null check (length(trim(vendor)) > 0),
    category text,
    amount_minor_units bigint not null check (amount_minor_units >= 0),
    currency_code text not null check (currency_code ~ '^[A-Z]{3}$'),
    due_date date not null,
    recurrence text not null default 'one_time' check (
        recurrence in ('one_time', 'weekly', 'monthly', 'quarterly', 'yearly')
    ),
    status text not null default 'planned'
        check (status in ('planned', 'paid', 'cancelled')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index expenses_business_due_date_idx
    on public.expenses (business_id, due_date);

create table public.reminders (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null
        references public.businesses (id) on delete cascade,
    invoice_id uuid not null
        references public.invoices (id) on delete cascade,
    draft_text text not null check (length(trim(draft_text)) > 0),
    status text not null default 'draft' check (
        status in (
            'draft',
            'pending_approval',
            'approved',
            'sending',
            'sent',
            'failed',
            'cancelled'
        )
    ),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index reminders_business_status_idx
    on public.reminders (business_id, status);
create index reminders_invoice_id_idx on public.reminders (invoice_id);

create table public.reminder_approvals (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null
        references public.businesses (id) on delete restrict,
    reminder_id uuid not null unique
        references public.reminders (id) on delete restrict,
    approved_by text not null check (length(trim(approved_by)) > 0),
    approved_at timestamptz not null default now(),
    note text
);

create index reminder_approvals_business_id_idx
    on public.reminder_approvals (business_id);

create table public.reminder_send_attempts (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null
        references public.businesses (id) on delete restrict,
    reminder_id uuid not null
        references public.reminders (id) on delete restrict,
    attempted_at timestamptz not null default now(),
    status text not null check (status in ('succeeded', 'failed')),
    provider_request_id text,
    error_code text,
    error_message text
);

create index reminder_send_attempts_reminder_id_idx
    on public.reminder_send_attempts (reminder_id);
create index reminder_send_attempts_business_id_idx
    on public.reminder_send_attempts (business_id);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create or replace function public.prevent_mutation()
returns trigger
language plpgsql
as $$
begin
    raise exception 'Table % is append-only.', tg_table_name;
end;
$$;

create trigger businesses_set_updated_at
    before update on public.businesses
    for each row execute function public.set_updated_at();

create trigger customers_set_updated_at
    before update on public.customers
    for each row execute function public.set_updated_at();

create trigger invoices_set_updated_at
    before update on public.invoices
    for each row execute function public.set_updated_at();

create trigger expenses_set_updated_at
    before update on public.expenses
    for each row execute function public.set_updated_at();

create trigger reminders_set_updated_at
    before update on public.reminders
    for each row execute function public.set_updated_at();

create trigger reminder_approvals_prevent_mutation
    before update or delete on public.reminder_approvals
    for each row execute function public.prevent_mutation();

create trigger reminder_send_attempts_prevent_mutation
    before update or delete on public.reminder_send_attempts
    for each row execute function public.prevent_mutation();
