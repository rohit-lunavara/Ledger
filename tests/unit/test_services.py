from decimal import InvalidContext
from ledger.domain.bucket import AccountingBucket
import pytest

from ledger.service_layer.services import (InvalidIdentifier, create_bucket, is_valid_identifier)

class TestIsValidIdentifier:
    def test_identifier_invalid_if_smaller_than_min_length(self):
        assert is_valid_identifier('', []) is False
    
    def test_identifier_invalid_if_larger_than_max_length(self):
        assert is_valid_identifier('test-bucket-name' * 10000, []) is False

    def test_identifier_invalid_if_bucket_with_identifier_already_exists(self):
        test_bucket = AccountingBucket.create('test-bucket-name')
        assert is_valid_identifier('test-bucket-name', [test_bucket]) is False

    def test_identifier_valid_if_no_bucket_with_identifier_already_exists(self):
        test_bucket = AccountingBucket.create('test-bucket-name')
        other_test_bucket = AccountingBucket.create('other-test-bucket-name')
        assert is_valid_identifier('new-test-bucket-name', [test_bucket, other_test_bucket])

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