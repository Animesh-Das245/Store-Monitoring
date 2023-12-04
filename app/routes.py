from flask import Blueprint, jsonify, send_file
from .report_generator import generate_report
import os
import uuid

main = Blueprint('main', __name__)

@main.route('/trigger_report', methods=['GET'])
def trigger_report():
    report_id = str(uuid.uuid4())
    generate_report(report_id)
    return jsonify({'report_id': report_id})

@main.route('/get_report/<report_id>', methods=['GET'])
def get_report(report_id):
    report_path = f'reports/{report_id}.csv'
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    else:
        return jsonify({'status': 'Running'})
