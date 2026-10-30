
WITH accounts AS (
    SELECT * FROM read_csv_auto('data/raw/accounts.csv')
),
payments AS (
    SELECT * FROM read_csv_auto('data/raw/payments.csv')
),
calls AS (
    SELECT * FROM read_csv_auto('data/raw/calls.csv')
),
agents AS (
    SELECT * FROM read_csv_auto('data/raw/agents.csv')
)
SELECT
    'payments' AS dataset,
    COUNT(*) AS raw_rows,
    COUNT(DISTINCT payment_id) AS distinct_keys,
    COUNT(*) - COUNT(DISTINCT payment_id) AS duplicate_rows
FROM payments
UNION ALL
SELECT
    'calls',
    COUNT(*),
    COUNT(DISTINCT call_id),
    COUNT(*) - COUNT(DISTINCT call_id)
FROM calls
UNION ALL
SELECT
    'agents',
    COUNT(*),
    COUNT(DISTINCT agent_id),
    COUNT(*) - COUNT(DISTINCT agent_id)
FROM agents;
