# Data Cleaning and Golden Dataset

## Scope

The supplied dataset contains January 2026 through August 2026 event data. August is partial through 8 August, so trend conclusions use January through July as the comparable full-month period.

## Source-of-truth decisions

`accounts.account_id` is the portfolio entity key. `accounts.borrower_id` is the borrower identifier used for account-level analysis because event tables contain large borrower-ID inconsistencies.

`payment_id` is the payment event key. Duplicate payment rows are collapsed to one record per payment ID.

`call_id` is the call event key. Duplicate call rows are collapsed to one record per call ID, preferring the record with a populated agent ID where the duplicate differs.

`agent_id` is the operational agent key. The agents table contains multiple snapshots per agent and changing employee codes, so the latest `updated_at` record is retained for the agent master.

## Deduplication

Payment duplicates are identified by repeated `payment_id`. Exact duplicate rows are removed. For the 14 non-identical duplicate payment IDs, the only differing field is `payment_reference`, so the non-null reference is retained.

Call duplicates are identified by repeated `call_id`. Exact duplicates are removed. Seventy-nine duplicate call IDs contain conflicting event time or agent ID values. These are flagged because there is no event version field to prove which record is authoritative.

WhatsApp duplicate event IDs are removed at the event level.

## Borrower entity resolution

Most event tables contain borrower IDs that disagree with the borrower ID stored on the account. The account relationship is therefore treated as the stronger analytical key. Event borrower IDs are not used to join portfolio attributes.

## Timestamp treatment

Timestamps are parsed as datetimes. The supplied files contain explicit timezone fields, but call timezone disagrees with vendor timezone on a large share of records. The analysis therefore does not silently rewrite historical timestamps. Monthly trend reporting uses the timestamp as supplied and records timezone inconsistency as a data-quality limitation.

## Payment attribution

Recovery is defined independently from campaign attribution: successful payment amount by payment event month. For targeting analysis, the first targeting event for each account is used and successful payments in the following 14 days are attributed to that first target. This avoids counting the same payment against multiple target events.

## Missing data

Missing payment references do not invalidate a payment when `payment_id` is present. Missing agent IDs are retained for call-level metrics but cannot support agent attribution. Missing client and language dimensions are treated as schema limitations.

## Exclusions

Rows without a valid account relationship are excluded from account-level golden metrics. Partial August is shown for completeness but excluded from the main month-over-month conclusion.

## Golden layer

The main analytical table is `data/golden/golden_account_month.csv`. It contains one row per account per reporting month and joins portfolio attributes with successful payment activity, call activity, and first-target information.
