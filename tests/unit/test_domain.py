import pytest

from ledger.domain.bucket import AccountingBucket

class TestCreateAccountingBucket:
    def test_new_bucket_created_for_valid_identifier(self):
        bucket = AccountingBucket.create(identifier='loan-commitment-liability')

        assert isinstance(bucket, AccountingBucket)
        assert bucket.debit == 0.0
        assert bucket.credit == 0.0

class TestAccountingBucketAddValue:
    def test_if_value_is_debit_then_debit_amount_incremented(self):
        bucket = AccountingBucket.create(identifier='test-bucket')
        bucket.add_value(1.0)

        assert bucket.debit == 1.0
        assert bucket.credit == 0.0

    def test_if_value_is_credit_then_credit_amount_incremented(self):
        bucket = AccountingBucket.create(identifier='test-bucket')
        bucket.add_value(-1.0)

        assert bucket.debit == 0.0
        assert bucket.credit == -1.0

    def test_if_value_is_zero_then_no_amount_is_changed(self):
        bucket = AccountingBucket.create(identifier='test-bucket')
        bucket.add_value(0.0)

        assert bucket.debit == 0.0
        assert bucket.credit == 0.0