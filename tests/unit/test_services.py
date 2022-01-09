from datetime import date
import pytest

from ledger.domain.bucket import (AccountingBucket, LedgerEntry)
from ledger.service_layer.services import (InvalidIdentifier, InvalidPairValue, create_bucket, create_double_entries, create_ledger_entry, is_bucket_present, is_valid_new_identifier, is_valid_pair_value)

class TestIsValidIdentifier:
    def test_identifier_invalid_if_smaller_than_min_length(self):
        assert is_valid_new_identifier('', []) is False
    
    def test_identifier_invalid_if_larger_than_max_length(self):
        assert is_valid_new_identifier('test-bucket-name' * 10000, []) is False

    def test_identifier_invalid_if_bucket_with_identifier_already_exists(self):
        test_bucket = AccountingBucket.create('test-bucket-name')
        assert is_valid_new_identifier('test-bucket-name', [test_bucket]) is False

    def test_identifier_valid_if_no_bucket_with_identifier_already_exists(self):
        test_bucket = AccountingBucket.create('test-bucket-name')
        other_test_bucket = AccountingBucket.create('other-test-bucket-name')
        assert is_valid_new_identifier('new-test-bucket-name', [test_bucket, other_test_bucket])

class TestCreateBucket:
    def test_if_invalid_identifier_then_error_raised(self):
        test_bucket = AccountingBucket.create('test-bucket-name')

        with pytest.raises(InvalidIdentifier):
            _ = create_bucket('test-bucket-name', [test_bucket])

    def test_if_valid_identifier_then_bucket_created(self):
        test_bucket = AccountingBucket.create('test-bucket-name')

        new_bucket = create_bucket('other-test-bucket-name', [test_bucket])

        assert isinstance(new_bucket, AccountingBucket)
        assert new_bucket.identifier == 'other-test-bucket-name'

class TestIsBucketPresent:
    def test_if_no_bucket_with_identifier_present_then_bucket_not_present(self):
        test_bucket = AccountingBucket.create('test-bucket-name')
        assert is_bucket_present('other-test-bucket-name', [test_bucket]) is False

    def test_if_bucket_with_identifier_present_then_bucket_present(self):
        test_bucket = AccountingBucket.create('test-bucket-name')
        assert is_bucket_present('test-bucket-name', [test_bucket])

class TestCreateLedgerEntry:
    def test_if_no_buckets_then_error_raised(self):
        with pytest.raises(InvalidIdentifier):
            _ = create_ledger_entry(1, 'test-bucket-name', 100.0, date.today(), [])

    def test_if_invalid_bucket_then_error_raised(self):
        test_bucket = AccountingBucket.create('test-bucket-name')

        with pytest.raises(InvalidIdentifier):
            _ = create_ledger_entry(1, 'other-test-bucket-name', 100.0, date.today(), [test_bucket])

    def test_if_valid_bucket_then_ledger_entry_is_created(self):
        test_bucket = AccountingBucket.create('test-bucket-name')

        ledger_entry = create_ledger_entry(1, 'test-bucket-name', 100.0, date.today(), [test_bucket])

        assert isinstance(ledger_entry, LedgerEntry)
        assert ledger_entry.effective_date == date.today()

class TestIsValidPairValue:
    def test_if_unequal_values_then_invalid(self):
        assert is_valid_pair_value(0.2, 0.1) is False

    def test_if_zero_values_then_valid(self):
        assert is_valid_pair_value(0.0, 0.0)

    def test_if_equal_and_opposite_values_flipped_then_valid(self):
        assert is_valid_pair_value(-0.1, 0.1) is False

    def test_if_equal_and_opposite_values_then_valid(self):
        assert is_valid_pair_value(0.1, -0.1)

class TestCreateDoubleEntries:
    def test_if_no_pair_entries_then_no_double_entries_created(self):
        ledger_entries = create_double_entries(1, [], [])
        assert not ledger_entries

    def test_if_pair_entries_with_invalid_values_then_error_raised(self):
        test_debit_bucket = AccountingBucket.create('test-debit-bucket')
        test_credit_bucket = AccountingBucket.create('test-credit-bucket')
        pair_entries = [
            {
                "effective_date": "2021-01-21",
                "debit": {
                    "identifier": "test-debit-bucket",
                    "value": 123.0
                },
                "credit": {
                    "identifier": "test-credit-bucket",
                    "value": 123.0
                }
            }
        ]
        with pytest.raises(InvalidPairValue):
            _ = create_double_entries(1, pair_entries, [test_debit_bucket, test_credit_bucket])


    def test_if_pair_entries_with_invalid_bucket_then_error_raised(self):
        test_debit_bucket = AccountingBucket.create('test-debit-bucket')
        test_credit_bucket = AccountingBucket.create('test-credit-bucket')
        pair_entries = [
            {
                "effective_date": "2021-01-21",
                "debit": {
                    "identifier": "test-debit-bucket",
                    "value": 123.0
                },
                "credit": {
                    "identifier": "test-credit-bucket",
                    "value": -123.0
                }
            }
        ]
        with pytest.raises(InvalidIdentifier):
            _ = create_double_entries(1, pair_entries, [test_debit_bucket])

    
    def test_if_pair_entries_valid_then_double_entries_created(self):
        test_debit_bucket = AccountingBucket.create('test-debit-bucket')
        test_credit_bucket = AccountingBucket.create('test-credit-bucket')
        other_test_credit_bucket = AccountingBucket.create('other-test-credit-bucket')
        pair_entries = [
            {
                "effective_date": "2022-01-21",
                "debit": {
                    "identifier": "test-debit-bucket",
                    "value": 123.0
                },
                "credit": {
                    "identifier": "test-credit-bucket",
                    "value": -123.0
                }
            },
            {
                "debit": {
                    "identifier": "test-debit-bucket",
                    "value": 100.0
                },
                "credit": {
                    "identifier": "other-test-credit-bucket",
                    "value": -100.0
                }
            }
        ]
        ledger_entries = create_double_entries(1, pair_entries, [test_debit_bucket, test_credit_bucket, other_test_credit_bucket])
        assert len(ledger_entries) == 4

        future_date = date.fromisoformat("2022-01-21")
        assert ledger_entries[0].value == 123.0 and ledger_entries[0].bucket_identifier == "test-debit-bucket" and ledger_entries[0].effective_date == future_date
        assert ledger_entries[1].value == -123.0 and ledger_entries[1].bucket_identifier == "test-credit-bucket" and ledger_entries[1].effective_date == future_date
        assert ledger_entries[2].value == 100.0 and ledger_entries[2].bucket_identifier == "test-debit-bucket" and ledger_entries[2].effective_date == date.today()
        assert ledger_entries[3].value == -100.0 and ledger_entries[3].bucket_identifier == "other-test-credit-bucket" and ledger_entries[3].effective_date == date.today()