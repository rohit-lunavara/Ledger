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

    # TODO: Add test with ledger entries

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
        success_response = client.post('/ledger/buckets?identifier=test-debit-bucket')
        assert 'created successfully' in success_response.get_json()['message']
        assert success_response.status_code == 200

        failure_response = client.post('/ledger/buckets?identifier=test-debit-bucket')
        assert 'please provide a unique value' in failure_response.get_json()['error']
        assert failure_response.status_code == 400