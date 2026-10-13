from fastapi import FastAPI
from pydantic import BaseModel, Field
from reconciliation.engine import reconcile
from reconciliation.models import Transaction, ReconciliationReport

app = FastAPI(title="Intelligent Payment Reconciliation", version="0.1.0",
              description="Educational API for deterministic reconciliation of synthetic payment records.")

class ReconcileRequest(BaseModel):
    ledger: list[Transaction]
    processor: list[Transaction]
    date_tolerance_minutes: int = Field(default=10, ge=0, le=1440)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reconcile", response_model=ReconciliationReport)
def run_reconciliation(request: ReconcileRequest) -> ReconciliationReport:
    return reconcile(request.ledger, request.processor, request.date_tolerance_minutes)
