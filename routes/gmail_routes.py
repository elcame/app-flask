from flask import Blueprint, render_template, request, jsonify
from services.gmail_service import GmailService
from flask_login import login_required
from datetime import datetime

gmail_bp = Blueprint('gmail_bp', __name__)
gmail_service = GmailService()

@gmail_bp.route('/gmail')
@login_required
def gmail_dashboard():
    return render_template('gmail/dashboard.html')

@gmail_bp.route('/gmail/search', methods=['POST'])
@login_required
def search_emails():
    data = request.get_json()
    query = data.get('query', '')
    max_results = data.get('max_results', 10)
    
    emails = gmail_service.get_emails(query=query, max_results=max_results)
    return jsonify(emails)

@gmail_bp.route('/gmail/search-by-date', methods=['POST'])
@login_required
def search_by_date():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    emails = gmail_service.search_emails_by_date(start_date, end_date)
    return jsonify(emails)

@gmail_bp.route('/gmail/search-by-sender', methods=['POST'])
@login_required
def search_by_sender():
    data = request.get_json()
    sender_email = data.get('sender_email')
    
    emails = gmail_service.search_emails_by_sender(sender_email)
    return jsonify(emails) 