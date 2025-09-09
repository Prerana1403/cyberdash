from flask import Blueprint, render_template, jsonify, redirect, send_file
from .nessus_client import NessusAPI
import os, time, xml.etree.ElementTree as ET

# Create blueprint
nessus2_bp = Blueprint('nessus2', __name__, template_folder='templates/nessus2')

NESSUS_URL = os.getenv('NESSUS_URL', 'https://localhost:8834')
ACCESS_KEY = os.getenv('NESSUS_ACCESS_KEY', 'd9f5cf021cc4a2cc7eacca517c038dab531f8eb4db50b536c8f77de0fcf2642a')
SECRET_KEY = os.getenv('NESSUS_SECRET_KEY', '219ab7d47ec079f376fe3ec5f404420d113cbf70b07e610732628a40ec6af085')

nessus = NessusAPI(NESSUS_URL, ACCESS_KEY, SECRET_KEY)

# --- Parser function ---

def parse_nessus_summary(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    summary = {
        "hosts": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for report_host in root.findall(".//ReportHost"):
        summary["hosts"] += 1
        for report_item in report_host.findall("ReportItem"):
            severity = int(report_item.get("severity", 0))
            if severity == 4:
                summary["critical"] += 1
            elif severity == 3:
                summary["high"] += 1
            elif severity == 2:
                summary["medium"] += 1
            elif severity == 1:
                summary["low"] += 1
    return summary


# --- Routes ---
@nessus2_bp.route('/nessus2_home')
def list_scans():
    scans = nessus.list_scans()
    return render_template('scans.html', scans=scans)

@nessus2_bp.route('/scan/<int:scan_id>/summary')
def scan_summary(scan_id):
    file_path = os.path.join(EXPORT_DIR, f'scan_{scan_id}.nessus')
    if not os.path.exists(file_path):
        return jsonify({'error': 'No export file found. Please export first.'}), 404

    summary = parse_nessus_summary(file_path)
    return render_template('scan_summary.html', summary=summary, scan_id=scan_id)

@nessus2_bp.route('/scan/<int:scan_id>')
def scan_details(scan_id):
    details = nessus.get_scan_details(scan_id)
    scan_id = details.get('info', {}).get('object_id', scan_id)  # fallback
    scan_name = details.get('info', {}).get('name', f"Scan {scan_id}")
    return render_template('scan_details.html', scan=details, scan_id=scan_id, scan_name=scan_name)

@nessus2_bp.route('/scan/<int:scan_id>/status')
def scan_status(scan_id):
    return jsonify({'status': nessus.get_scan_status(scan_id)})

@nessus2_bp.route('/scan/<int:scan_id>/open')
def open_gui(scan_id):
    return redirect(f'{NESSUS_URL}/scans/{scan_id}')

EXPORT_DIR = os.path.join(os.path.dirname(__file__), 'exports')
os.makedirs(EXPORT_DIR, exist_ok=True)

@nessus2_bp.route('/scan/<int:scan_id>/export', methods=['GET'])
def export_scan(scan_id):
    try:
        file_id = nessus.request_export(scan_id)
        for _ in range(10):  # poll until ready
            status = nessus.check_export_status(scan_id, file_id)
            if status == 'ready':
                data = nessus.download_export(scan_id, file_id)
                file_path = os.path.join(EXPORT_DIR, f'scan_{scan_id}.nessus')
                with open(file_path, 'wb') as f:
                    f.write(data)
                # let user download directly
                return send_file(file_path, as_attachment=True)
            time.sleep(2)
        return jsonify({'error': 'Export timeout'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500
