from app import app
from models import db
import models.user_model
import models.ping_model
import models.nmap_model

with app.app_context():
    db.create_all()
    print("All tables created in cyberdash.db")
