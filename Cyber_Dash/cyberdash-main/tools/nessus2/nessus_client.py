import requests
import urllib3

# Disable SSL warnings (because Nessus uses self-signed certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NessusAPI:
    def __init__(self, url, access_key, secret_key):
        self.url = url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = False  # accept Nessus self-signed cert
        self.session.headers.update({
            "X-ApiKeys": f"accessKey={access_key}; secretKey={secret_key}",
            "Content-Type": "application/json"
        })

    # ✅ List all scans
    def list_scans(self):
        resp = self.session.get(f"{self.url}/scans")
        resp.raise_for_status()
        return resp.json().get("scans", [])

    # ✅ Get scan details
    def get_scan_details(self, scan_id):
        resp = self.session.get(f"{self.url}/scans/{scan_id}")
        resp.raise_for_status()
        return resp.json()

    # ✅ Get scan status
    def get_scan_status(self, scan_id):
        details = self.get_scan_details(scan_id)
        return details.get("info", {}).get("status", "unknown")

    # ✅ Request export
    def request_export(self, scan_id, format="nessus"):
        resp = self.session.post(f"{self.url}/scans/{scan_id}/export",
                                 json={"format": format})
        resp.raise_for_status()
        return resp.json()["file"]

    # ✅ Check export status
    def check_export_status(self, scan_id, file_id):
        resp = self.session.get(f"{self.url}/scans/{scan_id}/export/{file_id}/status")
        resp.raise_for_status()
        return resp.json()["status"]

    # ✅ Download exported report
    def download_export(self, scan_id, file_id):
        resp = self.session.get(f"{self.url}/scans/{scan_id}/export/{file_id}/download")
        resp.raise_for_status()
        return resp.content
