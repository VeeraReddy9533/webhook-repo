from flask import Blueprint, json, request, jsonify, render_template
from pymongo import MongoClient

# Connect to MongoDB
mongo = MongoClient('mongodb://localhost:27017/')
db = mongo['webhookdata']


webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')

@webhook_bp.route('/data', methods=['GET'])
def display_webhook_data():
    latest_webhooks = list(db.webhook_events.find())
    return render_template('webhook.html', webhooks=latest_webhooks)

@webhook_bp.route('/receiver', methods=["POST"])
def receiver():
    payload = request.json
    action = payload['action']
    author = payload['sender'].get('login', 'Unknown')
    pull_request = payload['pull_request']
    from_branch = pull_request.get('head', {}).get('ref', 'Unknown')
    to_branch = pull_request.get('base', {}).get('ref', 'Unknown')
    timestamp = pull_request.get('created_at', 'Unknown')
    try:
        db.webhook_events.insert_one({
            'author': author,
            'action': action,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        })
        return jsonify({'message': 'Webhook received'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


