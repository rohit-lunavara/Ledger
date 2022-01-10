from flask import (Flask, request, jsonify)
from ledger.adapters.repository import LedgerRepository
from ledger.domain import bucket

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

@app.route('/ledger/entries', methods=['POST'])
def create_double_entries():
    loan_id = request.args.get('loan_id', type=int)
    if not loan_id:
        return jsonify({'error': 'Please enter a valid integer loan id'}), 400

    entries = request.get_json()
    for entry in entries:
        debit_entry = entry.get('debit', None)
        credit_entry = entry.get('credit', None)
        if not debit_entry or not credit_entry:
            return jsonify({'error': 'Please provide valid debit and credit objects for each pair entry'}), 400

        if not isinstance(debit_entry['value'], float) or not isinstance(credit_entry['value'], float):
            return jsonify({'error': 'Please provide valid floating point value for each pair entry'}), 400

    bucket_repo = repositories['bucket']
    try:
        ledger_entries = services.create_double_entries(loan_id, entries, bucket_repo.get())
    except (services.InvalidDate, services.InvalidPairValue, services.InvalidIdentifier) as e:
        return jsonify({'error': str(e)}), 400
    
    ledger_repo = repositories['ledger']
    ledger_repo.add(ledger_entries)

    return jsonify({'message': f'"{len(ledger_entries)}" ledger entries created successfully'}), 200

@app.route('/ledger/buckets/sum', methods=['GET'])
def get_buckets_sum():
    loan_id = request.args.get('loan_id', type=int)
    if not loan_id:
        return jsonify({'error': 'Please enter a valid integer loan id'}), 400

    bucket_identifiers = request.args.getlist('bucket_id', type=str)
    if not bucket_identifiers:
        return jsonify({'error': 'Please enter at least one bucket identifier'}), 400

    bucket_repo = repositories['bucket']
    ledger_repo = repositories['ledger']
    try:
        buckets_sum = services.get_buckets_sum(loan_id, bucket_identifiers, bucket_repo.get(), ledger_repo.get())
    except services.InvalidIdentifier as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'entries': buckets_sum}), 200



@app.route('/ledger/entries', methods=['GET'])
def get_ledger_entries():
    loan_id = request.args.get('loan_id', type=int)
    if not loan_id:
        return jsonify({'error': 'Please enter a valid integer loan id'}), 400

    ledger_repo = repositories['ledger']
    ledger_entries = services.get_ledger_entries(loan_id, ledger_repo.get())
    return jsonify({'entries': ledger_entries}), 200