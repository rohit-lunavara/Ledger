from dataclasses import dataclass
from datetime import date
from typing import Iterator, List, Optional

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

    def get_all_entries(self) -> Iterator[LedgerEntry]:
        yield from self.entries

    def get_entries(self, loan_id: Optional[int], identifiers: List[str]) -> Iterator[LedgerEntry]:
        loan_id_check = lambda entry: True
        if loan_id:
            loan_id_check = lambda entry: entry.loan_id == loan_id

        identifiers_check = lambda entry: True
        if identifiers:
            identifiers_check = lambda entry: entry.bucket_identifier in identifiers

        for entry in self.get_all_entries():
            if loan_id_check(entry) and identifiers_check(entry):
                yield entry


    def get_entries_by_loan_id(self, loan_id: int) -> Iterator[LedgerEntry]:
        return (entry for entry in self.entries if entry.loan_id == loan_id)

    def get_entries_by_bucket_identifier(self, identifier: str) -> Iterator[LedgerEntry]:
        return (entry for entry in self.entries if entry.bucket_identifier == identifier)
