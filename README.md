# CredResolve Data Analyst Assignment

This repository answers the four core questions in the assignment using the supplied collections dataset.

## Executive finding

The reported “11% month-on-month recovery improvement” is not a sustained trend. March 2026 is +11.03% versus February, but January to July recovery is 0.01% higher overall. August is partial through 8 August and is excluded from the main trend.

The recommended investment area is **better borrower targeting**, with a controlled experiment required before committing the full ₹10 Cr.

## Repository structure

```text
credresolve_data_analyst_submission/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   │   ├── accounts.csv
│   │   ├── agents.csv
│   │   ├── agent_sessions.csv
│   │   ├── borrowers.csv
│   │   ├── call_attempts.csv
│   │   ├── call_dispositions.csv
│   │   ├── calls.csv
│   │   ├── campaigns.csv
│   │   ├── complaints.csv
│   │   ├── daily_targeting.csv
│   │   ├── field_visits.csv
│   │   ├── payments.csv
│   │   ├── promises_to_pay.csv
│   │   ├── sms_events.csv
│   │   ├── vendor_telephony.csv
│   │   └── whatsapp_events.csv
│   ├── golden/
│   │   ├── golden_account_month.csv
│   │   ├── monthly_metrics.csv
│   │   ├── first_target_account.csv
│   │   ├── borrower_master.csv
│   │   └── agent_master.csv
│   └── quality/
│       └── data_quality_report.csv
├── src/
│   └── build_golden.py
├── sql/
│   ├── 01_data_quality.sql
│   ├── 02_golden_metrics.sql
│   └── 03_investment_analysis.sql
├── analysis/
│   └── analysis.ipynb
├── dashboard/
│   └── executive_dashboard.html
├── docs/
│   ├── architecture.mmd
│   ├── architecture.svg
│   ├── architecture_decision.md
│   ├── counterfactual_methodology.md
│   ├── data_cleaning.md
│   └── executive_memo.md
└── outputs/
    └── submission_summary.txt
```

## Run locally

Python 3.10+ is recommended.

```bash
pip install -r requirements.txt
python src/build_golden.py
```

Open `analysis/analysis.ipynb` in Jupyter and run the notebook from the repository root.

The build script automatically extracts the supplied dataset zip into data/raw before processing. The SQL uses DuckDB and reads the extracted raw CSVs.

```bash
pip install duckdb
duckdb
```

Then run the SQL files in `sql/`.

Open `dashboard/executive_dashboard.html` in a browser for the one-screen executive dashboard.

## Metric definitions

Recovery amount is the sum of successful payment amounts by payment event month after payment deduplication.

Recovery rate is successful recovery divided by the fixed portfolio outstanding amount in the supplied accounts table.

Contact rate is unique accounts with an answered outbound call divided by unique accounts with an outbound call.

RPC is a conservative proxy based on answered outbound calls with a qualifying disposition rather than `NO_CONTACT` or `WRONG_NUMBER`.

PTP rate is unique accounts with a `PTP` or `PROMISE_TO_PAY` disposition divided by RPC accounts.

PTP kept rate is kept PTPs divided by PTPs with a due date inside the observable period and status `KEPT` or `BROKEN`.

Target 14-day conversion is the share of accounts whose first targeting event is followed by at least one successful payment within 14 days.

## Important limitations

The supplied dataset covers January through August 2026, with August ending on 8 August. It does not contain a client identifier or language field. Cost data is also absent, so cost per ₹ recovered cannot be observed directly.

The investment ROI is therefore a scenario estimate and not a measured causal return.

## What to discuss in the interview

Be ready to explain why account-level borrower identity is trusted over event borrower IDs, how duplicate payments are removed, why August is excluded from the main trend, why the 11% claim is rejected as a sustained KPI, why targeting is a hypothesis rather than a causal conclusion, and how the proposed experiment would identify incremental recovery.
