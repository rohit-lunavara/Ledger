from datetime import date, datetime
from typing import (Dict, List, Optional)

from ledger import config
from ledger.domain.bucket import (AccountingBucket, LedgerEntry)

MINIMUM_IDENTIFIER_LENGTH = config.get_minimum_identifier_size()
MAXIMUM_IDENTIFIER_LENGTH = config.get_maximum_identifier_size()

def is_valid_new_identifier(identifier: str, buckets: List[AccountingBucket]) -> bool:
    if len(identifier) < MINIMUM_IDENTIFIER_LENGTH:
        return False
    if len(identifier) > MAXIMUM_IDENTIFIER_LENGTH:
        return False
    if any(identifier == bucket.identifier for bucket in buckets):
        return False
    return True

def is_bucket_present(identifier: str, buckets: List[AccountingBucket]) -> bool:
    return any(identifier == bucket.identifier for bucket in buckets)

def is_valid_pair_value(debit_value: float, credit_value: float) -> bool:
    if debit_value < 0 or credit_value > 0:
        return False
    return abs(debit_value) == abs(credit_value)

class InvalidIdentifier(ValueError):
    """Bucket identifier cannot be accepted"""
    pass

class InvalidPairValue(ValueError):
    """Pair value cannot be accepted"""
    pass

def create_bucket(identifier: str, buckets: List[AccountingBucket]) -> AccountingBucket: # uow: unit_of_work.AbstractUnitOfWork
    if not is_valid_new_identifier(identifier, buckets):
        raise InvalidIdentifier('Please provide a valid bucket identifier')
    
    return AccountingBucket.create(identifier)

def create_ledger_entry(loan_id: int, identifier: str, value: float, effective_date: date, buckets: List[AccountingBucket]) -> LedgerEntry:
    if not is_bucket_present(identifier, buckets):
        raise InvalidIdentifier('Please provide a bucket identifier which is already created')
    
    if not effective_date:
        effective_date = date.today()
    
    created_at = date.today()
    return LedgerEntry(loan_id, created_at, effective_date, identifier, value)

def create_double_entry(loan_id: int, pair_entries: List[Dict]) -> List[LedgerEntry]:
    ledger_entries = []
    for pair_entry in pair_entries:
        debit_entry = pair_entry['debit']
        credit_entry = pair_entry['credit']
        effective_date = pair_entry.get('effective_date', date.today())

        if not is_valid_pair_value(debit_entry['value'], credit_entry['value']):
            raise InvalidPairValue('Debit value must be positive, credit value must be negative and the absolute value must be equal to each other')
            
        # try:
        #     pass
        # except InvalidIdentifier as e:
        #     pass
