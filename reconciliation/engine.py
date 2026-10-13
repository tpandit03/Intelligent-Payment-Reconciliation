from collections import defaultdict
from datetime import datetime, timezone
from uuid import uuid4
from reconciliation.models import Transaction, ReconciliationItem, ReconciliationReport

def _utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def reconcile(ledger: list[Transaction], processor: list[Transaction],
              date_tolerance_minutes: int = 10) -> ReconciliationReport:
    # Explicit rules: duplicate references are exceptions; candidates are checked
    # for currency, amount, then timestamp; a processor row is consumed at most once.
    if date_tolerance_minutes < 0:
        raise ValueError("date_tolerance_minutes cannot be negative")

    by_ref = defaultdict(list)
    for idx, txn in enumerate(processor):
        by_ref[txn.reference].append((idx, txn))

    consumed: set[int] = set()
    items: list[ReconciliationItem] = []
    tolerance_seconds = date_tolerance_minutes * 60

    for led in ledger:
        candidates = by_ref.get(led.reference, [])
        if len(candidates) > 1:
            items.append(ReconciliationItem(
                ledger_transaction_id=led.transaction_id,
                processor_transaction_ids=[t.transaction_id for _, t in candidates],
                reference=led.reference, outcome="DUPLICATE_PROCESSOR_RECORD",
                reason=f"Found {len(candidates)} processor records for this reference; review required."))
            continue
        available = [(i, t) for i, t in candidates if i not in consumed]
        if not available:
            items.append(ReconciliationItem(
                ledger_transaction_id=led.transaction_id, reference=led.reference,
                outcome="MISSING_IN_PROCESSOR", reason="No processor record found for this reference."))
            continue

        idx, proc = available[0]
        if led.currency != proc.currency:
            outcome, reason = "CURRENCY_MISMATCH", f"Ledger currency {led.currency} differs from processor currency {proc.currency}."
        elif led.amount != proc.amount:
            outcome, reason = "AMOUNT_MISMATCH", f"Ledger amount {led.amount} differs from processor amount {proc.amount}."
        else:
            delta = abs((_utc(led.timestamp) - _utc(proc.timestamp)).total_seconds())
            if delta > tolerance_seconds:
                outcome, reason = "DATE_MISMATCH", f"Timestamp difference {int(delta)} seconds exceeds {date_tolerance_minutes}-minute tolerance."
            else:
                outcome, reason = "MATCHED", "Reference, amount, currency, and timestamp checks passed."
                consumed.add(idx)

        items.append(ReconciliationItem(
            ledger_transaction_id=led.transaction_id, processor_transaction_ids=[proc.transaction_id],
            reference=led.reference, outcome=outcome, reason=reason))

    for idx, proc in enumerate(processor):
        if idx in consumed:
            continue
        represented = any(proc.transaction_id in item.processor_transaction_ids for item in items)
        if not represented:
            items.append(ReconciliationItem(
                processor_transaction_ids=[proc.transaction_id], reference=proc.reference,
                outcome="UNMATCHED_PROCESSOR", reason="Processor record has no corresponding ledger match."))

    matched = sum(i.outcome == "MATCHED" for i in items)
    return ReconciliationReport(
        run_id=str(uuid4()), created_at=datetime.now(timezone.utc),
        ledger_count=len(ledger), processor_count=len(processor), matched_count=matched,
        exception_count=sum(i.outcome != "MATCHED" for i in items), items=items)
