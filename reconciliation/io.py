import csv
from pathlib import Path
from reconciliation.models import Transaction

def load_transactions(path: str | Path) -> list[Transaction]:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"transaction_id", "reference", "amount", "currency", "timestamp"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing CSV columns: {', '.join(sorted(missing))}")
        return [Transaction.model_validate(row) for row in reader]
