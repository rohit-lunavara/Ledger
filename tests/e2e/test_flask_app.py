import json
import pytest

from ledger.entrypoints.flask_app import app

# TODO: Find out why data saved between requests
@pytest.fixture()
def client():
    with app.test_client() as client:
        yield client

class TestGetLedgerEntries:
    def test_missing_loan_id_returns_400(self, client):
        response = client.get('/ledger/entries?loan_id=')
        assert 'loan id' in response.get_json()['error']
        assert response.status_code == 400

    def test_non_integer_loan_id_returns_400(self, client):
        response = client.get('/ledger/entries?loan_id=test-loan-id')
        assert 'loan id' in response.get_json()['error']
        assert response.status_code == 400

    def test_loan_id_found_returns_ledger_entries(self, client):
        response = client.get('/ledger/entries?loan_id=1')
        assert response.get_json()['entries'] == []
        assert response.status_code == 200

    def test_loan_id_with_entries_found_returns_ledger_entries(self, client):
        bucket_created_response = client.post('/ledger/buckets?identifier=test-entries-found-bucket')
        assert 'created successfully' in bucket_created_response.get_json()['message']
        assert bucket_created_response.status_code == 200

        entries = [
            {
                "effective_date": "2021-01-21",
                "debit": {
                    "identifier": "test-entries-found-bucket",
                    "value": 123.0
                },
                "credit": {
                    "identifier": "test-entries-found-bucket",
                    "value": -123.0
                }
            }
        ]
        response = client.post('/ledger/entries?loan_id=1', data=json.dumps(entries), content_type='application/json')
        assert '"2" ledger entries' in response.get_json()['message']
        assert response.status_code == 200

        response = client.get('/ledger/entries?loan_id=1')
        response_entries = response.get_json()['entries']
        assert response.status_code == 200
        assert len(response_entries) == 2
        
        debit_entry = response_entries[0]
        assert debit_entry['value'] == entries[0]['debit']['value']
        assert debit_entry['bucket_identifier'] == entries[0]['debit']['identifier']
        assert debit_entry['loan_id'] == 1

        credit_entry = response_entries[1]
        assert credit_entry['value'] == entries[0]['credit']['value']
        assert credit_entry['bucket_identifier'] == entries[0]['credit']['identifier']
        assert credit_entry['loan_id'] == 1

class TestCreateBucket:
    def test_missing_bucket_id_param_returns_400(self, client):
        response = client.post('/ledger/buckets?identifier=')
        assert 'bucket identifier' in response.get_json()['error']
        assert response.status_code == 400

    def test_unique_bucket_id_returns_200(self, client):
        success_response = client.post('/ledger/buckets?identifier=test-unique-bucket')
        assert 'created successfully' in success_response.get_json()['message']
        assert success_response.status_code == 200

    def test_existing_bucket_id_returns_400(self, client):
        success_response = client.post('/ledger/buckets?identifier=test-existing-bucket')
        assert 'created successfully' in success_response.get_json()['message']
        assert success_response.status_code == 200

        failure_response = client.post('/ledger/buckets?identifier=test-existing-bucket')
        assert 'please provide a unique value' in failure_response.get_json()['error']
        assert failure_response.status_code == 400

class TestCreateDoubleEntries:
    def test_missing_loan_id_returns_400(self, client):
        response = client.post('/ledger/entries?loan_id=')
        assert 'loan id' in response.get_json()['error']
        assert response.status_code == 400

    def test_non_integer_loan_id_returns_400(self, client):
        response = client.post('/ledger/entries?loan_id=test-loan-id')
        assert 'loan id' in response.get_json()['error']
        assert response.status_code == 400

    def test_inconsistent_pair_returns_400(self, client):
        entries = [
            {
                "effective_date": "2021-01-21",
                "debit": {
                    "identifier": "test-debit-bucket",
                    "value": 123.0
                }
            }
        ]
        response = client.post('/ledger/entries?loan_id=1', data=json.dumps(entries), content_type='application/json')
        assert 'debit and credit' in response.get_json()['error']
        assert response.status_code == 400

    def test_non_float_value_returns_400(self, client):
        entries = [
            {
                "effective_date": "2021-01-21",
                "debit": {
                    "identifier": "test-debit-bucket",
                    "value": "123.0"
                },
                "credit": {
                    "identifier": "test-credit-bucket",
                    "value": "-123.0"
                }
            }
        ]
        response = client.post('/ledger/entries?loan_id=1', data=json.dumps(entries), content_type='application/json')
        assert 'floating point value' in response.get_json()['error']
        assert response.status_code == 400

    def test_nonexistent_bucket_id_returns_400(self, client):
        entries = [
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
        response = client.post('/ledger/entries?loan_id=1', data=json.dumps(entries), content_type='application/json')
        assert 'bucket identifier' in response.get_json()['error']
        assert response.status_code == 400

    def test_proper_values_creates_entries_and_returns_200(self, client):
        debit_bucket_response = client.post('/ledger/buckets?identifier=test-proper-debit-bucket')
        assert debit_bucket_response.status_code == 200
        credit_bucket_response = client.post('/ledger/buckets?identifier=test-proper-credit-bucket')
        assert credit_bucket_response.status_code == 200

        entries = [
            {
                "effective_date": "2021-01-21",
                "debit": {
                    "identifier": "test-proper-debit-bucket",
                    "value": 123.0
                },
                "credit": {
                    "identifier": "test-proper-credit-bucket",
                    "value": -123.0
                }
            }
        ]
        response = client.post('/ledger/entries?loan_id=1', data=json.dumps(entries), content_type='application/json')
        assert '"2" ledger entries' in response.get_json()['message']
        assert response.status_code == 200

class TestGetBucketsSum:
    def test_missing_loan_id_returns_400(self, client):
        response = client.get('/ledger/buckets/sum?loan_id=')
        assert 'loan id' in response.get_json()['error']
        assert response.status_code == 400

    def test_non_integer_loan_id_returns_400(self, client):
        response = client.get('/ledger/buckets/sum?loan_id=test-loan-id')
        assert 'loan id' in response.get_json()['error']
        assert response.status_code == 400

    def test_missing_bucket_ids_returns_400(self, client):
        response = client.get('/ledger/buckets/sum?loan_id=1&bucket_ids=')
        assert 'bucket identifier' in response.get_json()['error']
        assert response.status_code == 400

    def test_loan_id_with_entries_found_returns_buckets_sum(self, client):
        debit_bucket_response = client.post('/ledger/buckets?identifier=test-new-debit-bucket')
        assert debit_bucket_response.status_code == 200
        credit_bucket_response = client.post('/ledger/buckets?identifier=test-new-credit-bucket')
        assert credit_bucket_response.status_code == 200

        entries = [
            {
                "effective_date": "2021-01-21",
                "debit": {
                    "identifier": "test-new-debit-bucket",
                    "value": 123.0
                },
                "credit": {
                    "identifier": "test-new-credit-bucket",
                    "value": -123.0
                }
            }
        ]
        entries_response = client.post('/ledger/entries?loan_id=1', data=json.dumps(entries), content_type='application/json')
        assert '"2" ledger entries' in entries_response.get_json()['message']
        assert entries_response.status_code == 200

        response = client.get('/ledger/buckets/sum?loan_id=1&bucket_id=test-new-debit-bucket&bucket_id=test-new-credit-bucket')
        print(response.get_json())
        assert response.status_code == 200
        buckets_sum = response.get_json()['entries']
        assert buckets_sum['test-new-debit-bucket'] == 123.0
        assert buckets_sum['test-new-credit-bucket'] == -123.0

