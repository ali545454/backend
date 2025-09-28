# models/admin.py
from app import db
from datetime import datetime
import uuid

class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # هيتخزن مشفر
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
