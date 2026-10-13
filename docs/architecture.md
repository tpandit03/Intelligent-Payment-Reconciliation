# Architecture

```text
Ledger CSV ─────┐
                ├─> CSV Loader + Pydantic validation
Processor CSV ──┘               |
                                v
                     Deterministic reconciliation
                     - reference candidate lookup
                     - duplicate detection
                     - currency / amount / time checks
                                |
                                v
                     Explainable report (JSON)
                       ├─ CLI
                       └─ FastAPI POST /reconcile
```

Inputs are untrusted. The starter has no authentication, persistent storage, or secrets management. Add those controls before deployment. Run IDs and report timestamps vary; matching outcomes are deterministic for the same input and configuration.
