
WITH payments AS (
    SELECT *
    FROM read_csv_auto('data/raw/payments.csv')
),
payment_dedup AS (
    SELECT *
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY payment_id
                ORDER BY payment_reference NULLS LAST, event_at
            ) AS rn
        FROM payments
    )
    WHERE rn = 1
),
monthly_recovery AS (
    SELECT
        DATE_TRUNC('month', CAST(event_at AS TIMESTAMP)) AS month,
        SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END) AS recovery_amount,
        COUNT(DISTINCT CASE WHEN payment_status = 'SUCCESS' THEN payment_id END) AS successful_payments,
        COUNT(DISTINCT CASE WHEN payment_status = 'SUCCESS' THEN account_id END) AS recovered_accounts
    FROM payment_dedup
    GROUP BY 1
)
SELECT
    month,
    recovery_amount,
    successful_payments,
    recovered_accounts,
    recovery_amount / NULLIF(LAG(recovery_amount) OVER (ORDER BY month), 0) - 1 AS mom_recovery_change
FROM monthly_recovery
ORDER BY month;
