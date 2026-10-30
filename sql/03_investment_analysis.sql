
WITH accounts AS (
    SELECT * FROM read_csv_auto('data/raw/accounts.csv')
),
payments AS (
    SELECT *
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY payment_id
                ORDER BY payment_reference NULLS LAST, event_at
            ) AS rn
        FROM read_csv_auto('data/raw/payments.csv')
    )
    WHERE rn = 1
),
campaigns AS (
    SELECT * FROM read_csv_auto('data/raw/campaigns.csv')
),
targeting AS (
    SELECT
        t.*,
        c.strategy_version,
        c.channel
    FROM read_csv_auto('data/raw/daily_targeting.csv') t
    LEFT JOIN campaigns c USING (campaign_id)
),
first_target AS (
    SELECT *
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY target_date) AS rn
        FROM targeting
    )
    WHERE rn = 1
),
target_recovery AS (
    SELECT
        t.account_id,
        t.strategy_version,
        t.channel,
        t.priority,
        SUM(CASE
            WHEN p.payment_status = 'SUCCESS'
             AND CAST(p.event_at AS TIMESTAMP) >= CAST(t.target_date AS TIMESTAMP)
             AND CAST(p.event_at AS TIMESTAMP) < CAST(t.target_date AS TIMESTAMP) + INTERVAL 14 DAY
            THEN p.amount ELSE 0 END) AS recovery_14d
    FROM first_target t
    LEFT JOIN payments p USING (account_id)
    GROUP BY 1,2,3,4
)
SELECT
    strategy_version,
    channel,
    COUNT(*) AS accounts,
    AVG(recovery_14d) AS avg_recovery_14d,
    AVG(CASE WHEN recovery_14d > 0 THEN 1 ELSE 0 END) * 100 AS conversion_pct
FROM target_recovery
GROUP BY 1,2
ORDER BY avg_recovery_14d DESC;
