insert into public.businesses (id, name, base_currency)
values (
    '11111111-1111-4111-8111-111111111111',
    'Bridgewater Design Studio',
    'USD'
)
on conflict (id) do nothing;

insert into public.customers (id, business_id, name)
values
    (
        '22222222-2222-4222-8222-222222222201',
        '11111111-1111-4111-8111-111111111111',
        'Northwind Retail'
    ),
    (
        '22222222-2222-4222-8222-222222222202',
        '11111111-1111-4111-8111-111111111111',
        'Kestrel Analytics'
    ),
    (
        '22222222-2222-4222-8222-222222222203',
        '11111111-1111-4111-8111-111111111111',
        'Harbor & Pine'
    )
on conflict (id) do nothing;

insert into public.invoices (
    id,
    business_id,
    customer_id,
    paypal_invoice_id,
    invoice_number,
    status,
    invoice_date,
    due_date,
    currency_code,
    total_minor_units,
    amount_due_minor_units
)
values
    (
        '33333333-3333-4333-8333-333333333301',
        '11111111-1111-4111-8111-111111111111',
        '22222222-2222-4222-8222-222222222201',
        'DEMO-INV-1001',
        'INV-1001',
        'PAID',
        '2026-09-01',
        '2026-09-15',
        'USD',
        250000,
        0
    ),
    (
        '33333333-3333-4333-8333-333333333302',
        '11111111-1111-4111-8111-111111111111',
        '22222222-2222-4222-8222-222222222202',
        'DEMO-INV-1002',
        'INV-1002',
        'SENT',
        '2026-09-20',
        '2026-10-15',
        'USD',
        120000,
        120000
    ),
    (
        '33333333-3333-4333-8333-333333333303',
        '11111111-1111-4111-8111-111111111111',
        '22222222-2222-4222-8222-222222222203',
        'DEMO-INV-1003',
        'INV-1003',
        'SENT',
        '2026-10-05',
        '2026-11-05',
        'USD',
        480000,
        480000
    ),
    (
        '33333333-3333-4333-8333-333333333304',
        '11111111-1111-4111-8111-111111111111',
        '22222222-2222-4222-8222-222222222201',
        'DEMO-INV-1004',
        'INV-1004',
        'DRAFT',
        '2026-10-20',
        '2026-11-20',
        'USD',
        90000,
        90000
    ),
    (
        '33333333-3333-4333-8333-333333333305',
        '11111111-1111-4111-8111-111111111111',
        '22222222-2222-4222-8222-222222222202',
        'DEMO-INV-1005',
        'INV-1005',
        'PARTIALLY_PAID',
        '2026-09-25',
        '2026-10-20',
        'USD',
        300000,
        150000
    ),
    (
        '33333333-3333-4333-8333-333333333306',
        '11111111-1111-4111-8111-111111111111',
        '22222222-2222-4222-8222-222222222203',
        'DEMO-INV-1006',
        'INV-1006',
        'PAID',
        '2026-08-15',
        '2026-08-30',
        'USD',
        75000,
        0
    )
on conflict (id) do nothing;

insert into public.expenses (
    id,
    business_id,
    vendor,
    category,
    amount_minor_units,
    currency_code,
    due_date,
    recurrence,
    status
)
values
    (
        '44444444-4444-4444-8444-444444444401',
        '11111111-1111-4111-8111-111111111111',
        'Maple Street Studios',
        'rent',
        350000,
        'USD',
        '2026-11-01',
        'monthly',
        'planned'
    ),
    (
        '44444444-4444-4444-8444-444444444402',
        '11111111-1111-4111-8111-111111111111',
        'LedgerKit',
        'software',
        12000,
        'USD',
        '2026-11-03',
        'monthly',
        'planned'
    ),
    (
        '44444444-4444-4444-8444-444444444403',
        '11111111-1111-4111-8111-111111111111',
        'Riverside Print Co.',
        'contractor',
        200000,
        'USD',
        '2026-11-10',
        'one_time',
        'planned'
    ),
    (
        '44444444-4444-4444-8444-444444444404',
        '11111111-1111-4111-8111-111111111111',
        'Beacon Mutual',
        'insurance',
        45000,
        'USD',
        '2026-12-01',
        'quarterly',
        'planned'
    ),
    (
        '44444444-4444-4444-8444-444444444405',
        '11111111-1111-4111-8111-111111111111',
        'Cedar Utilities',
        'utilities',
        18000,
        'USD',
        '2026-11-15',
        'monthly',
        'planned'
    )
on conflict (id) do nothing;

insert into public.reminders (
    id,
    business_id,
    invoice_id,
    draft_text,
    status
)
values
    (
        '55555555-5555-4555-8555-555555555501',
        '11111111-1111-4111-8111-111111111111',
        '33333333-3333-4333-8333-333333333302',
        'Hi Northwind Retail, this is a friendly reminder that invoice INV-1002 for $1,200.00 was due on October 15, 2026. Please let us know if you need a copy.',
        'pending_approval'
    ),
    (
        '55555555-5555-4555-8555-555555555502',
        '11111111-1111-4111-8111-111111111111',
        '33333333-3333-4333-8333-333333333303',
        'Hi Harbor & Pine, invoice INV-1003 for $4,800.00 is due on November 5, 2026. We would appreciate payment by the due date.',
        'draft'
    )
on conflict (id) do nothing;
