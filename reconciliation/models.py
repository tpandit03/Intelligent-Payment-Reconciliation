from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Transaction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transaction_id: str = Field(min_length=1, max_length=100)
    reference: str = Field(min_length=1, max_length=150)
    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)
    timestamp: datetime

    @field_validator("amount")
    @classmethod
    def finite_amount(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("amount must be finite")
        return value

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        value = value.strip().upper()
        if len(value) != 3 or not value.isalpha():
            raise ValueError("currency must be a three-letter code")
        return value

    @field_validator("reference")
    @classmethod
    def normalize_reference(cls, value: str) -> str:
        return value.strip()

Outcome = Literal["MATCHED", "AMOUNT_MISMATCH", "CURRENCY_MISMATCH", "DATE_MISMATCH",
                  "MISSING_IN_PROCESSOR", "DUPLICATE_PROCESSOR_RECORD", "UNMATCHED_PROCESSOR"]

class ReconciliationItem(BaseModel):
    ledger_transaction_id: str | None = None
    processor_transaction_ids: list[str] = Field(default_factory=list)
    reference: str
    outcome: Outcome
    reason: str

class ReconciliationReport(BaseModel):
    run_id: str
    created_at: datetime
    ledger_count: int
    processor_count: int
    matched_count: int
    exception_count: int
    items: list[ReconciliationItem]
