from models import db
from datetime import datetime


class ScanRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tool = db.Column(db.String(50))
    target = db.Column(db.String(255))
    scan_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    results_json = db.Column(db.Text)  # Store raw Nessus JSON output