from datetime import date
from typing import (Dict, List, Optional)

from ledger import config
from ledger.domain.ledger import (Ledger, LedgerEntry)
from ledger.domain.bucket import (AccountingBucket)

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

def get_bucket_by_identifier(identifier: str, buckets: List[AccountingBucket]) -> Optional[AccountingBucket]:
    return next((bucket for bucket in buckets if identifier == bucket.identifier), None)

class InvalidIdentifier(ValueError):
    """Bucket identifier cannot be accepted"""
    pass

class InvalidPairValue(ValueError):
    """Pair value cannot be accepted"""
    pass

class InvalidDate(ValueError):
    """String date value cannot be accepted"""
    pass

def create_bucket(identifier: str, buckets: List[AccountingBucket]) -> AccountingBucket: # uow: unit_of_work.AbstractUnitOfWork
    if not is_valid_new_identifier(identifier, buckets):
        raise InvalidIdentifier('Duplicate bucket identifier found, please provide a unique value')
    
    return AccountingBucket.create(identifier)

def create_ledger_entry(loan_id: int, identifier: str, value: float, effective_date: date, buckets: List[AccountingBucket]) -> LedgerEntry:
    if not is_bucket_present(identifier, buckets):
        raise InvalidIdentifier('Please provide a bucket identifier which is already created')

    current_bucket = get_bucket_by_identifier(identifier, buckets)
    current_bucket.add_value(value)

    created_at = date.today()
    return LedgerEntry(loan_id, created_at, effective_date, identifier, value)

def create_double_entries(loan_id: int, pair_entries: List[Dict], buckets: List[AccountingBucket]) -> List[LedgerEntry]:
    ledger_entries = []
    for pair_entry in pair_entries:
        debit_entry = pair_entry['debit']
        credit_entry = pair_entry['credit']

        if not pair_entry.get('effective_date'):
            effective_date = date.today()
        else:
            try:
                effective_date = date.fromisoformat(pair_entry['effective_date'])
            except ValueError as e:
                raise InvalidDate('Effective date value must be a string with YYYY-MM-DD format')

        if not is_valid_pair_value(debit_entry['value'], credit_entry['value']):
            raise InvalidPairValue('Debit value must be positive, credit value must be negative and the absolute value must be equal to each other')
            
        try:
            debit_ledger_entry = create_ledger_entry(loan_id, debit_entry['identifier'], debit_entry['value'], effective_date, buckets)
            credit_ledger_entry = create_ledger_entry(loan_id, credit_entry['identifier'], credit_entry['value'], effective_date, buckets)
        except InvalidIdentifier as e:
            raise e

        ledger_entries.append(debit_ledger_entry)
        ledger_entries.append(credit_ledger_entry)

    return ledger_entries

def get_ledger_entries(loan_id: int, ledger: Ledger) -> List[LedgerEntry]:
    return list(ledger.get_entries_by_loan_id(loan_id))


def get_buckets_sum(loan_id: int, identifiers: List[str], buckets: List[AccountingBucket], ledger: Ledger) -> Dict[str, float]:
    buckets_sum = {}
    for identifier in identifiers:
        print(identifier)
        if not is_bucket_present(identifier, buckets):
            raise InvalidIdentifier('Please provide a valid bucket identifier')

        ledger_entries = ledger.get_entries(loan_id, identifier)
        buckets_sum[identifier] = sum([entry.value for entry in ledger_entries])

    return buckets_sum