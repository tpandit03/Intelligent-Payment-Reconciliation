# Intelligent Payment Reconciliation

A runnable Python reference implementation that compares internal-ledger transactions with payment-processor records and reports matches and exceptions.

> Educational reference implementation using synthetic data only. Not a certified banking system. Do not use with real customer/payment data without security, compliance, resilience, and operational reviews.

## Features
- Deterministic reference-based matching
- Amount, currency, and timestamp tolerance checks
- Duplicate, missing, and unmatched record detection
- FastAPI endpoint and command-line runner
- Decimal arithmetic, synthetic sample CSVs, tests, architecture notes

## Run locally (Python 3.11+)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m reconciliation.cli --ledger data/internal_ledger.csv --processor data/payment_processor.csv --output reports/report.json
uvicorn reconciliation.api:app --reload
```
API docs: http://127.0.0.1:8000/docs

## API
`POST /reconcile` accepts `ledger`, `processor`, and optional `date_tolerance_minutes` fields. See `tests/test_api.py` for a working example.

## Outcomes
`MATCHED`, `AMOUNT_MISMATCH`, `CURRENCY_MISMATCH`, `DATE_MISMATCH`, `MISSING_IN_PROCESSOR`, `DUPLICATE_PROCESSOR_RECORD`, `UNMATCHED_PROCESSOR`.

## Production extensions
Add authentication, authorization, durable storage, signed audit events, provider-specific parsers, reversals/refunds/chargebacks, monitoring, retention policies, and human-review workflows before production use.
