from flask import (Flask, request, jsonify)
from ledger.adapters.repository import LedgerRepository

from ledger.service_layer import services
from ledger.adapters import repository

app = Flask(__name__)
repositories = {
    'ledger': repository.LedgerRepository(),
    'loan': repository.LoanRepository(),
    'bucket': repository.BucketRepository(),
}

@app.route('/ledger/buckets', methods=['POST'])
def create_bucket():
    bucket_identifier = request.args.get('identifier', type=str)
    if not bucket_identifier:
        return jsonify({'error': 'Please enter a valid string bucket identifier'}), 400

    bucket_repo = repositories['bucket']
    try:
        new_bucket = services.create_bucket(bucket_identifier, bucket_repo.get())
    except services.InvalidIdentifier as e:
        return jsonify({'error': str(e)}), 400
    
    bucket_repo.add(new_bucket)
    return jsonify({'message': f'Bucket named "{bucket_identifier}" created successfully'}), 200


@app.route('/ledger/entries', methods=['GET'])
def get_ledger_entries():
    loan_id = request.args.get('loan_id', type=int)
    if not loan_id:
        return jsonify({'error': 'Please enter a valid integer loan id'}), 400

    ledger_repo = repositories['ledger']
    ledger_entries = services.get_ledger_entries(loan_id, ledger_repo.get())
    return jsonify({'entries': ledger_entries}), 200