import pytest

from ledger.domain.bucket import AccountingBucket

class TestAccountingBucket:
    def test_new_bucket_created_for_valid_identifier(self):
        bucket = AccountingBucket.create(identifier='loan-commitment-liability')

        assert isinstance(bucket, AccountingBucket)
        assert bucket.debit == 0.0
        assert bucket.credit == 0.0