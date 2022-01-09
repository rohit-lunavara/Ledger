from typing import List, Tuple

from ledger import config
from ledger.domain.bucket import AccountingBucket

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

class InvalidIdentifier(ValueError):
    """Bucket identifier cannot be accepted"""
    pass

def create_bucket(identifier: str, buckets: List[AccountingBucket]) -> AccountingBucket: # uow: unit_of_work.AbstractUnitOfWork
    if not is_valid_new_identifier(identifier, buckets):
        raise InvalidIdentifier()
    
    return AccountingBucket.create(identifier)