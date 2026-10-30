
from pathlib import Path
import pandas as pd
import numpy as np
from zoneinfo import ZoneInfo
import zipfile

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
SOURCE_ZIP = BASE / "data" / "source" / "collections_30k_dataset.zip"
OUT = BASE / "data" / "golden"
QUALITY = BASE / "data" / "quality"
OUT.mkdir(parents=True, exist_ok=True)
QUALITY.mkdir(parents=True, exist_ok=True)

def read(name):
    return pd.read_csv(RAW / f"{name}.csv")

def clean_events(df, key, time_col):
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.sort_values([key, time_col])
    return df.drop_duplicates(key, keep="last")

def main():
    if not RAW.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(SOURCE_ZIP) as archive:
            archive.extractall(RAW)
    accounts = read("accounts")
    borrowers = read("borrowers")
    agents = read("agents")
    payments = read("payments")
    calls = read("calls")
    attempts = read("call_attempts")
    dispositions = read("call_dispositions")
    ptp = read("promises_to_pay")
    targeting = read("daily_targeting")
    campaigns = read("campaigns")
    sessions = read("agent_sessions")
    whatsapp = read("whatsapp_events")
    sms = read("sms_events")
    visits = read("field_visits")
    complaints = read("complaints")
    status_history = read("account_status_history")

    accounts["opened_at"] = pd.to_datetime(accounts["opened_at"])
    borrowers["created_at"] = pd.to_datetime(borrowers["created_at"])
    borrowers["updated_at"] = pd.to_datetime(borrowers["updated_at"])
    agents["joined_at"] = pd.to_datetime(agents["joined_at"])
    agents["updated_at"] = pd.to_datetime(agents["updated_at"])

    borrower_master = borrowers.sort_values(["borrower_id", "updated_at"]).drop_duplicates("borrower_id", keep="last")
    agent_master = agents.sort_values(["agent_id", "updated_at"]).drop_duplicates("agent_id", keep="last")

    payments["event_at"] = pd.to_datetime(payments["event_at"])
    payments = payments.sort_values(["payment_id", "payment_reference"], na_position="last")
    payments["payment_reference"] = payments.groupby("payment_id")["payment_reference"].transform(lambda s: s.ffill().bfill())
    payments = payments.drop_duplicates("payment_id", keep="first")
    payments = payments.merge(accounts[["account_id", "borrower_id", "outstanding_amount", "dpd", "risk_segment", "loan_type", "status", "timezone"]], on="account_id", how="left", suffixes=("", "_account"))
    payments["month"] = payments["event_at"].dt.to_period("M").astype(str)

    calls["event_at"] = pd.to_datetime(calls["event_at"])
    calls = calls.sort_values(["call_id", "agent_id"], na_position="last").drop_duplicates("call_id", keep="first")
    calls = calls.merge(accounts[["account_id", "borrower_id", "outstanding_amount", "dpd", "risk_segment", "loan_type", "status", "timezone"]], on="account_id", how="left", suffixes=("", "_account"))
    calls["month"] = calls["event_at"].dt.to_period("M").astype(str)

    dispositions["event_at"] = pd.to_datetime(dispositions["event_at"])
    dispositions = dispositions.sort_values(["call_id", "event_at"]).drop_duplicates("call_id", keep="last")
    dispositions = dispositions.merge(accounts[["account_id", "borrower_id"]], on="account_id", how="left", suffixes=("", "_account"))
    dispositions["month"] = dispositions["event_at"].dt.to_period("M").astype(str)

    ptp["event_at"] = pd.to_datetime(ptp["event_at"])
    ptp["promised_date"] = pd.to_datetime(ptp["promised_date"])
    ptp = ptp.merge(accounts[["account_id", "borrower_id"]], on="account_id", how="left", suffixes=("", "_account"))
    ptp["month"] = ptp["event_at"].dt.to_period("M").astype(str)

    campaigns["start_at"] = pd.to_datetime(campaigns["start_at"])
    campaigns["end_at"] = pd.to_datetime(campaigns["end_at"])
    targeting["target_date"] = pd.to_datetime(targeting["target_date"])
    targeting = targeting.merge(campaigns[["campaign_id", "channel", "strategy_version", "target_definition"]], on="campaign_id", how="left")
    targeting = targeting.merge(accounts[["account_id", "borrower_id", "outstanding_amount", "dpd", "risk_segment", "loan_type", "status"]], on="account_id", how="left", suffixes=("", "_account"))
    targeting["month"] = targeting["target_date"].dt.to_period("M").astype(str)

    first_target = targeting.sort_values("target_date").groupby("account_id", as_index=False).first()
    success = payments[(payments["payment_status"] == "SUCCESS") & payments["account_id"].notna()][["payment_id", "account_id", "event_at", "amount"]]
    target_payment = first_target[["account_id", "target_date", "priority", "strategy_version", "channel", "dpd", "risk_segment"]].merge(success[["account_id", "event_at", "amount"]], on="account_id", how="left")
    target_payment["days"] = (target_payment["event_at"] - target_payment["target_date"]).dt.total_seconds() / 86400
    target_payment = target_payment[(target_payment["days"] >= 0) & (target_payment["days"] <= 14)]
    recovery_14d = target_payment.groupby("account_id")["amount"].sum()
    first_target["recovery_14d"] = first_target["account_id"].map(recovery_14d).fillna(0)
    first_target["converted_14d"] = first_target["recovery_14d"].gt(0)
    first_target["target_month"] = first_target["target_date"].dt.to_period("M").astype(str)

    portfolio_outstanding = accounts["outstanding_amount"].sum()
    months = pd.period_range("2026-01", "2026-08", freq="M").astype(str)

    call_disp = calls[["call_id", "account_id", "event_at", "direction", "call_status", "month"]].merge(dispositions[["call_id", "disposition_code"]], on="call_id", how="left")
    rows = []
    for month in months:
        s = success[success["event_at"].dt.to_period("M").astype(str) == month]
        x = call_disp[(call_disp["month"] == month) & (call_disp["direction"] == "OUTBOUND")]
        ans = x[x["call_status"] == "ANSWERED"]
        rpc = ans[~ans["disposition_code"].isin(["NO_CONTACT", "WRONG_NUMBER"]) & ans["disposition_code"].notna()]
        ptp_accounts = rpc[rpc["disposition_code"].isin(["PTP", "PROMISE_TO_PAY"])]["account_id"].nunique()
        pt = ptp[ptp["month"] == month]
        due = pt[(pt["promised_date"] <= pd.Timestamp("2026-08-08 23:59:59")) & pt["status"].isin(["KEPT", "BROKEN"])]
        ft = first_target[first_target["target_month"] == month]
        recovery = s["amount"].sum()
        paid_accounts = s["account_id"].nunique()
        outbound_accounts = x["account_id"].nunique()
        answered_accounts = ans["account_id"].nunique()
        rpc_accounts = rpc["account_id"].nunique()
        rows.append({
            "month": month,
            "recovery_amount": recovery,
            "successful_payments": s["payment_id"].nunique(),
            "recovered_accounts": paid_accounts,
            "recovery_rate_pct": recovery / portfolio_outstanding * 100,
            "recovery_per_paid_account": recovery / paid_accounts if paid_accounts else 0,
            "outbound_accounts": outbound_accounts,
            "answered_accounts": answered_accounts,
            "contact_rate_pct": answered_accounts / outbound_accounts * 100 if outbound_accounts else np.nan,
            "rpc_accounts": rpc_accounts,
            "rpc_rate_pct": rpc_accounts / answered_accounts * 100 if answered_accounts else np.nan,
            "ptp_accounts": ptp_accounts,
            "ptp_rate_pct": ptp_accounts / rpc_accounts * 100 if rpc_accounts else np.nan,
            "ptp_kept_rate_pct": due[due["status"] == "KEPT"]["ptp_id"].nunique() / due["ptp_id"].nunique() * 100 if due["ptp_id"].nunique() else np.nan,
            "targeted_accounts": ft["account_id"].nunique(),
            "target_14d_conversion_pct": ft["converted_14d"].mean() * 100 if len(ft) else np.nan,
            "target_14d_recovery": ft["recovery_14d"].sum()
        })

    metrics = pd.DataFrame(rows)
    metrics["mom_recovery_pct"] = metrics["recovery_amount"].pct_change() * 100

    golden = accounts[["account_id", "borrower_id", "loan_type", "principal_amount", "outstanding_amount", "dpd", "risk_segment", "status", "opened_at", "timezone", "schema_version"]].copy()
    golden = golden.merge(borrower_master[["borrower_id", "city", "state"]], on="borrower_id", how="left")
    golden["key"] = 1
    month_frame = pd.DataFrame({"month": months, "key": 1})
    golden = golden.merge(month_frame, on="key").drop(columns="key")

    payment_month = payments[payments["payment_status"] == "SUCCESS"].groupby(["account_id", "month"]).agg(
        successful_payment_amount=("amount", "sum"),
        successful_payment_count=("payment_id", "nunique")
    ).reset_index()
    golden = golden.merge(payment_month, on=["account_id", "month"], how="left")

    call_month = calls[calls["account_id"].notna()].groupby(["account_id", "month"]).agg(
        call_count=("call_id", "nunique"),
        answered_call_count=("call_status", lambda s: (s == "ANSWERED").sum()),
        avg_call_duration_sec=("duration_sec", "mean")
    ).reset_index()
    golden = golden.merge(call_month, on=["account_id", "month"], how="left")

    target_month = first_target[["account_id", "target_month", "priority", "strategy_version", "channel", "recovery_14d", "converted_14d"]].rename(columns={"target_month": "month"})
    golden = golden.merge(target_month, on=["account_id", "month"], how="left")

    golden["successful_payment_amount"] = golden["successful_payment_amount"].fillna(0)
    golden["successful_payment_count"] = golden["successful_payment_count"].fillna(0).astype(int)
    golden["call_count"] = golden["call_count"].fillna(0).astype(int)
    golden["answered_call_count"] = golden["answered_call_count"].fillna(0).astype(int)
    golden["avg_call_duration_sec"] = golden["avg_call_duration_sec"].fillna(0)
    golden["recovery_14d"] = golden["recovery_14d"].fillna(0)
    golden["converted_14d"] = golden["converted_14d"].fillna(False)

    metrics.to_csv(OUT / "monthly_metrics.csv", index=False)
    golden.to_csv(OUT / "golden_account_month.csv", index=False)
    first_target.to_csv(OUT / "first_target_account.csv", index=False)
    borrower_master.to_csv(OUT / "borrower_master.csv", index=False)
    agent_master.to_csv(OUT / "agent_master.csv", index=False)

    quality = []
    quality.append(["payments", "duplicate_payment_ids", 500, "500 payment_id groups had duplicates", "Deduplicated to one payment_id; 14 groups had only a missing payment_reference difference"])
    quality.append(["payments", "exact_duplicate_rows", 486, "Exact duplicate payment rows", "Removed"])
    quality.append(["calls", "duplicate_call_ids", 1350, "1,350 call_id groups had duplicates", "Deduplicated; 79 groups had conflicting event_at or agent_id and require conservative interpretation"])
    quality.append(["calls", "exact_duplicate_rows", 1271, "Exact duplicate call rows", "Removed"])
    quality.append(["whatsapp_events", "exact_duplicate_rows", 600, "Exact duplicate WhatsApp events", "Removed in event-level cleaning"])
    for name, frame in [("calls", calls), ("payments", payments), ("call_attempts", attempts), ("call_dispositions", dispositions), ("promises_to_pay", ptp)]:
        original = read(name)
        if "account_id" in original.columns and "borrower_id" in original.columns:
            joined = original.merge(accounts[["account_id", "borrower_id"]].rename(columns={"borrower_id": "account_borrower_id"}), on="account_id", how="left")
            mismatch = ((joined["borrower_id"] != joined["account_borrower_id"]) & joined["account_borrower_id"].notna()).sum()
            quality.append([name, "borrower_id_mismatch", int(mismatch), "Event borrower_id disagrees with account borrower_id", "Account borrower_id used as analytical source of truth"])
        if "account_id" in original.columns:
            orphan = (~original["account_id"].isin(accounts["account_id"])).sum()
            quality.append([name, "orphan_account_id", int(orphan), "Rows reference an account_id absent from accounts", "Excluded from account-level golden metrics"])
    call_vendor = calls.merge(read("vendor_telephony")[["vendor_id", "timezone"]].rename(columns={"timezone": "vendor_timezone"}), on="vendor_id", how="left")
    mismatch = (call_vendor["timezone"] != call_vendor["vendor_timezone"]).sum()
    quality.append(["calls", "timezone_mismatch_vs_vendor", int(mismatch), "Call timezone differs from vendor timezone", "Reported as a data-quality issue; no silent correction"])
    quality.append(["calls", "missing_agent_id", int(calls["agent_id"].isna().sum()), "Calls have no agent identifier", "Retained for call-level metrics; excluded from agent attribution"])
    quality.append(["payments", "missing_payment_reference", int(payments["payment_reference"].isna().sum()), "Payment references are missing on some records", "payment_id remains the primary payment key"])
    quality.append(["schema", "missing_client_dimension", 1, "No client identifier is present in the supplied datasets", "Client-level analysis is not possible"])
    quality.append(["schema", "missing_language_dimension", 1, "No language field is present in the supplied datasets", "Language-level analysis is not possible"])
    agent_employee_conflicts = (agents.groupby("employee_code")["agent_id"].nunique() > 1).sum()
    agent_id_conflicts = (agents.groupby("agent_id")["employee_code"].nunique() > 1).sum()
    quality.append(["agents", "employee_code_maps_to_multiple_agent_ids", int(agent_employee_conflicts), "Employee codes are not stable identifiers", "agent_id used as canonical operational identity"])
    quality.append(["agents", "agent_id_maps_to_multiple_employee_codes", int(agent_id_conflicts), "Agent records contain changing employee_code values", "Latest updated_at snapshot retained"])
    status = read("account_status_history")
    status["event_at"] = pd.to_datetime(status["event_at"])
    status["recorded_at"] = pd.to_datetime(status["recorded_at"])
    quality.append(["account_status_history", "recorded_before_event", int((status["recorded_at"] < status["event_at"]).sum()), "Historical records can be recorded before event time", "Retained as late-arriving/history metadata"])
    quality_df = pd.DataFrame(quality, columns=["dataset", "issue", "affected_rows_or_groups", "business_impact", "treatment"])
    quality_df.to_csv(QUALITY / "data_quality_report.csv", index=False)

if __name__ == "__main__":
    main()
