import argparse
import json
from pathlib import Path
from reconciliation.engine import reconcile
from reconciliation.io import load_transactions

def main():
    parser = argparse.ArgumentParser(description="Reconcile ledger and processor CSV files.")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--processor", required=True)
    parser.add_argument("--output", default="reports/reconciliation_report.json")
    parser.add_argument("--date-tolerance-minutes", type=int, default=10)
    args = parser.parse_args()
    report = reconcile(load_transactions(args.ledger), load_transactions(args.processor), args.date_tolerance_minutes)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    print(f"Run: {report.run_id}\nMatched: {report.matched_count}\nExceptions: {report.exception_count}\nReport: {output}")

if __name__ == "__main__":
    main()
