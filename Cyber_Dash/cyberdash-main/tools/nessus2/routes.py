from flask import Blueprint, render_template, jsonify, redirect
from .nessus_client import NessusAPI
import os, time

# Create blueprint
nessus2_bp = Blueprint('nessus2', __name__, template_folder='templates/nessus2')

NESSUS_URL = os.getenv('NESSUS_URL', 'https://localhost:8834')
ACCESS_KEY = os.getenv('NESSUS_ACCESS_KEY', 'bffd5d8516dc46c447b9e3e11651700502d1abc83f31e27eae5824837ade3e52')
SECRET_KEY = os.getenv('NESSUS_SECRET_KEY', '6fc4a711e9cf6f427e653fb58c710a8b268c931cd800ebb15c55b747d2c5bcd2')

nessus = NessusAPI(NESSUS_URL, ACCESS_KEY, SECRET_KEY)

# Routes
@nessus2_bp.route('/nessus2_home')
def list_scans():
    scans = nessus.list_scans()
    return render_template('scans.html', scans=scans)

@nessus2_bp.route('/scan/<int:scan_id>')
def scan_details(scan_id):
    details = nessus.get_scan_details(scan_id)
    return render_template('scan_details.html', scan=details)

@nessus2_bp.route('/scan/<int:scan_id>/status')
def scan_status(scan_id):
    return jsonify({'status': nessus.get_scan_status(scan_id)})

@nessus2_bp.route('/scan/<int:scan_id>/open')
def open_gui(scan_id):
    return redirect(f'{NESSUS_URL}/scans/{scan_id}')

@nessus2_bp.route('/scan/<int:scan_id>/export', methods=['POST'])
def export_scan(scan_id):
    try:
        file_id = nessus.request_export(scan_id)
        for _ in range(10):  # poll until ready
            status = nessus.check_export_status(scan_id, file_id)
            if status == 'ready':
                data = nessus.download_export(scan_id, file_id)
                with open(f'scan_{scan_id}.nessus', 'wb') as f:
                    f.write(data)
                return jsonify({'message': f'Scan exported: scan_{scan_id}.nessus'})
            time.sleep(2)
        return jsonify({'error': 'Export timeout'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500
