import requests
import time
import urllib3

urllib3.disable_warnings()  # Disable SSL warnings for self-signed certs

class NessusAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = self._login(username, password)

    def _login(self, username, password):
        url = f'{self.base_url}/session'
        response = self.session.post(url, json={'username': username, 'password': password}, verify=False)
        response.raise_for_status()
        token = response.json()['token']
        self.session.headers.update({'X-Cookie': f'token={token}'})
        return token

    def list_scans(self):
        url = f'{self.base_url}/scans'
        response = self.session.get(url, verify=False)
        response.raise_for_status()
        return response.json()['scans']

    def get_scan_details(self, scan_id):
        url = f'{self.base_url}/scans/{scan_id}'
        response = self.session.get(url, verify=False)
        response.raise_for_status()
        return response.json()

    def get_scan_status(self, scan_id):
        details = self.get_scan_details(scan_id)
        return details['info']['status']  # e.g., "completed", "running"

    def request_export(self, scan_id, format='nessus'):
        url = f'{self.base_url}/scans/{scan_id}/export'
        response = self.session.post(url, json={'format': format}, verify=False)
        response.raise_for_status()
        return response.json()['file']

    def check_export_status(self, scan_id, file_id):
        url = f'{self.base_url}/scans/{scan_id}/export/{file_id}/status'
        response = self.session.get(url, verify=False)
        response.raise_for_status()
        return response.json()['status']  # e.g., "ready"

    def download_export(self, scan_id, file_id):
        url = f'{self.base_url}/scans/{scan_id}/export/{file_id}/download'
        response = self.session.get(url, verify=False)
        response.raise_for_status()
        return response.content
