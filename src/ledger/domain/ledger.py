from dataclasses import dataclass
from datetime import date
from typing import List

@dataclass(frozen=True)
class LedgerEntry:
    loan_id: int
    created_at: date
    effective_date: date
    bucket_identifier: str
    value: float


class Ledger:
    def __init__(self):
        self.entries = [] # type: List[LedgerEntry]

    def add_new_entries(self, new_entries: List[LedgerEntry]):
        self.entries.extend(new_entries)

    def get_all_entries(self) -> List[LedgerEntry]:
        return self.entries

    def get_entries(self, loan_id: int) -> List[LedgerEntry]:
        return [entry for entry in self.entries if entry.loan_id == loan_id]
