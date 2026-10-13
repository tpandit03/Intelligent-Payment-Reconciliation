from datetime import datetime, timezone
from decimal import Decimal
import pytest
from reconciliation.engine import reconcile
from reconciliation.models import Transaction

def txn(tid, ref, amount="10.00", currency="USD", minute=0):
    return Transaction(transaction_id=tid, reference=ref, amount=Decimal(amount), currency=currency,
                       timestamp=datetime(2026, 10, 1, 10, minute, tzinfo=timezone.utc))

def test_exact_match():
    report = reconcile([txn("L1", "R1")], [txn("P1", "R1", minute=2)])
    assert report.matched_count == 1
    assert report.items[0].outcome == "MATCHED"

def test_amount_mismatch():
    assert reconcile([txn("L1", "R1")], [txn("P1", "R1", "11.00")]).items[0].outcome == "AMOUNT_MISMATCH"

def test_missing_processor():
    assert reconcile([txn("L1", "R1")], []).items[0].outcome == "MISSING_IN_PROCESSOR"

def test_duplicate_reference():
    result = reconcile([txn("L1", "R1")], [txn("P1", "R1"), txn("P2", "R1")])
    assert result.items[0].outcome == "DUPLICATE_PROCESSOR_RECORD"

def test_currency_mismatch():
    assert reconcile([txn("L1", "R1")], [txn("P1", "R1", currency="EUR")]).items[0].outcome == "CURRENCY_MISMATCH"

def test_date_mismatch():
    assert reconcile([txn("L1", "R1")], [txn("P1", "R1", minute=30)]).items[0].outcome == "DATE_MISMATCH"

def test_unmatched_processor():
    assert reconcile([], [txn("P1", "ORPHAN")]).items[0].outcome == "UNMATCHED_PROCESSOR"

def test_negative_tolerance_rejected():
    with pytest.raises(ValueError):
        reconcile([], [], -1)
