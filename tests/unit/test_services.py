from ledger.domain.bucket import AccountingBucket
import pytest

from ledger.service_layer.services import (create_bucket, is_valid_identifier)

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
    pass