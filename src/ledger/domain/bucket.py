from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class LedgerEntry:
    loan_id: int
    created_at: date
    effective_date: date
    bucket_identifier: str
    value: float


class AccountingBucket:
    def __init__(self, identifier: str):
        self.identifier = identifier
        self.debit = 0.0
        self.credit = 0.0

    def is_debit_value(self, value: float):
        return value >= 0.0

    def is_credit_value(self, value: float):
        return value <= 0.0

    def add_value(self, value: float):
        if self.is_debit_value(value):
            self.debit += value
        elif self.is_credit_value(value):
            self.credit += value

    @classmethod
    def create(cls, identifier):
        """
        Creates a new accounting bucket with
        given identifier

        Args:
            identifier(str): Identifier for the accounting bucket
        Returns:
            bucket(AccountingBucket): New AccountingBucket with
                the given identifier
        """
        return cls(identifier)