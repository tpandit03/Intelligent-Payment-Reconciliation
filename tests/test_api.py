from fastapi.testclient import TestClient
from reconciliation.api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_reconcile_endpoint():
    payload = {
      "ledger": [{"transaction_id":"L1","reference":"R1","amount":"25.00","currency":"USD","timestamp":"2026-10-01T10:00:00Z"}],
      "processor": [{"transaction_id":"P1","reference":"R1","amount":"25.00","currency":"USD","timestamp":"2026-10-01T10:02:00Z"}],
      "date_tolerance_minutes": 10
    }
    response = client.post("/reconcile", json=payload)
    assert response.status_code == 200
    assert response.json()["matched_count"] == 1
