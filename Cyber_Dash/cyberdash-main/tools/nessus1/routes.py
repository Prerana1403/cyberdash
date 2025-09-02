import os
import xml.etree.ElementTree as ET
from flask import Blueprint, render_template, request, redirect, url_for, flash

nessus1_bp = Blueprint('nessus1', __name__, template_folder='templates/nessus1')

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Parser function
def parse_nessus(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    summary_data = []

    for report_host in root.findall(".//ReportHost"):
        host_ip = report_host.attrib.get("name", "Unknown")
        host_properties = {tag.attrib['name']: tag.text for tag in report_host.findall("HostProperties/tag")}
        os_name = host_properties.get("operating-system", "Unknown OS")

        findings = []
        for item in report_host.findall("ReportItem"):
            findings.append({
                "plugin": item.attrib.get("pluginName", "Unknown Plugin"),
                "severity": item.attrib.get("severity", "0"),
                "port": item.attrib.get("port", "N/A"),
                "protocol": item.attrib.get("protocol", "N/A"),
                "description": item.findtext("description", "").strip()
            })

        summary_data.append({
            "host_ip": host_ip,
            "os": os_name,
            "findings": findings
        })

    return summary_data

# Routes
@nessus1_bp.route('/nessus_home')
def nessus_home():
    return render_template('nessus_dashboard.html')

@nessus1_bp.route('/nessus/upload', methods=['GET', 'POST'])
def nessus_upload():
    if request.method == 'POST':
        file = request.files['nessus_file']
        if file and file.filename.endswith('.nessus'):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            summary = parse_nessus(filepath)
            return render_template('nessus_results.html', report=summary)
        else:
            flash("Please upload a valid .nessus file", "error")
            return redirect(url_for('nessus.nessus_upload'))
    return render_template('nessus_dashboard.html')

@nessus1_bp.route('/nessus/analyze', methods=['POST'])
def analyze_nessus():
    file = request.files.get('nessus_file')
    if not file or not file.filename.endswith('.nessus'):
        flash("Please upload a valid .nessus file", "error")
        return redirect(url_for('nessus.nessus_home'))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    parsed_data = parse_nessus(filepath)
    print(parsed_data)
    return render_template('nessus_scan_results.html', report=parsed_data)