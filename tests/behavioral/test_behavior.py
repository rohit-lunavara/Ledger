from datetime import datetime, date, timedelta
import json
import math
import pytest

from ledger.entrypoints.flask_app import app

# TODO: Find out why data saved between requests
@pytest.fixture()
def client():
    with app.test_client() as client:
        yield client

def create_buckets(client):
    buckets = [
        'accounts-receivable-principal',
        'accounts-receivable-interest',
        'income-interest',
        'future-receivable-principal',
        'loan-commitment-liability',
        'cash',
    ]
    for bucket in buckets:
        success_response = client.post(f'/ledger/buckets?identifier={bucket}')
        assert 'created successfully' in success_response.get_json()['message']
        assert success_response.status_code == 200

def originate_loan(client):
    entries = [
        {
            "debit": {
                "identifier": "loan-commitment-liability",
                "value": 1100.0
            },
            "credit": {
                "identifier": "future-receivable-principal",
                "value": -1100.0
            }
        },
        {
            "debit": {
                "identifier": "accounts-receivable-principal",
                "value": 1100.0
            },
            "credit": {
                "identifier": "cash",
                "value": -1100.0
            }
        }
    ]
    response = client.post('/ledger/entries?loan_id=123', data=json.dumps(entries), content_type='application/json')
    assert '"4" ledger entries' in response.get_json()['message']
    assert response.status_code == 200

def activate_loan(client):
    entries = [
        {
            "effective_date": "2021-01-21",
            "debit": {
                "identifier": "future-receivable-principal",
                "value": 1100.0
            },
            "credit": {
                "identifier": "loan-commitment-liability",
                "value": -1100.0
            }
        }
    ]
    response = client.post('/ledger/entries?loan_id=123', data=json.dumps(entries), content_type='application/json')
    assert '"2" ledger entries' in response.get_json()['message']
    assert response.status_code == 200

def accrue_interest(client):
    for day_delta in range(1, 60 + 1):
        entries = [
            {
                "effective_date": datetime.strftime(date.today() + timedelta(days=day_delta), '%Y-%m-%d'),
                "debit": {
                    "identifier": "accounts-receivable-interest",
                    "value": 0.241095
                },
                "credit": {
                    "identifier": "income-interest",
                    "value": -0.241095
                }
            },
        ]
        response = client.post('/ledger/entries?loan_id=123', data=json.dumps(entries), content_type='application/json')
        assert '"2" ledger entries' in response.get_json()['message']
        assert response.status_code == 200

class TestSixtyDayLoanPeriod:
    def test_accounts_are_balanced_for_loan(self, client):
        create_buckets(client)

        originate_loan(client)

        activate_loan(client)

        accrue_interest(client)

        buckets = [
            'accounts-receivable-principal',
            'accounts-receivable-interest',
            'income-interest',
            'future-receivable-principal',
            'loan-commitment-liability',
            'cash',
        ]
        bucket_ids = '&'.join((f'bucket_id={bucket_id}' for bucket_id in buckets))
        response = client.get(f'/ledger/buckets/sum?loan_id=123&{bucket_ids}')
        assert response.status_code == 200

        buckets_sum = response.get_json()['entries']
        assert buckets_sum['accounts-receivable-principal'] == 1100.0
        assert math.isclose(buckets_sum['accounts-receivable-interest'], 14.4657)
        assert math.isclose(buckets_sum['income-interest'], -14.4657)
        assert buckets_sum['future-receivable-principal'] == 0.0
        assert buckets_sum['loan-commitment-liability'] == 0.0
        assert buckets_sum['cash'] == -1100.0