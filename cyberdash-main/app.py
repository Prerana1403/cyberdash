from flask import Flask, render_template, jsonify, redirect
from nessus_client import NessusAPI
import os, time

app = Flask(__name__)

# Config: Change these to your Nessus login info
NESSUS_URL = os.getenv('NESSUS_URL', 'https://localhost:8834')
NESSUS_USER = os.getenv('NESSUS_USER', 'DRDLproject2025')
NESSUS_PASS = os.getenv('NESSUS_PASS', 'DRDLproject2025')

nessus = NessusAPI(NESSUS_URL, NESSUS_USER, NESSUS_PASS)

@app.route('/')
def list_scans():
    scans = nessus.list_scans()
    return render_template('scans.html', scans=scans)

@app.route('/scan/<int:scan_id>')
def scan_details(scan_id):
    details = nessus.get_scan_details(scan_id)
    return render_template('scan_details.html', scan=details)

@app.route('/scan/<int:scan_id>/status')
def scan_status(scan_id):
    return jsonify({'status': nessus.get_scan_status(scan_id)})

@app.route('/scan/<int:scan_id>/open')
def open_gui(scan_id):
    return redirect(f'{NESSUS_URL}/scans/{scan_id}')

@app.route('/scan/<int:scan_id>/export', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
