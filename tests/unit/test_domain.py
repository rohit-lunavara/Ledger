from datetime import date
import pytest

from ledger.domain.ledger import Ledger, LedgerEntry
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

class TestGetEntriesLedger:
    def test_if_ledger_empty_no_entries_returned(self):
        ledger = Ledger()
        ledger_entries = ledger.get_entries(1)
        assert not ledger_entries

    def test_if_loan_id_not_found_no_entries_returned(self):
        ledger = Ledger()
        ledger.add_new_entries([
            LedgerEntry(1, date.today(), date.today(), 'test-debit-bucket', 100.0)
        ])
        ledger_entries = ledger.get_entries(10000)
        assert not ledger_entries

    def test_if_loan_id_found_all_entries_returned(self):
        ledger = Ledger()
        ledger.add_new_entries([
            LedgerEntry(1, date.today(), 'test-debit-bucket', 100.0, date.today()),
            LedgerEntry(1, date.today(), 'test-debit-bucket', 100.0, date.today())
            ])

        ledger_entries = ledger.get_entries(1)
        assert len(ledger_entries) == 2