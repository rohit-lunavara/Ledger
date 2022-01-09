from typing import (Dict, List)

from ledger.domain import (ledger, bucket)

class LedgerRepository:
    def __init__(self):
        self.ledger = ledger.Ledger()

    def get(self) -> ledger.Ledger:
        return self.ledger

class LoanRepository:
    def __init__(self):
        self.loans = {} # type: Dict[int, List[bucket.AccountingBucket]]
    
    def get(self, loan_id: int) -> List[bucket.AccountingBucket]:
        return self.loans.get(loan_id, [])

class BucketRepository:
    def __init__(self):
        self.buckets = [] # type: List[bucket.AccountingBucket]

    def add(self, bucket: bucket.AccountingBucket):
        self.buckets.append(bucket)

    def get(self) -> List[bucket.AccountingBucket]:
        return self.buckets