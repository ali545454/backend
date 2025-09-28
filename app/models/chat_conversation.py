from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

class ChatConversation(db.Model):
    __tablename__ = "chat_conversations"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # علاقات
    student = db.relationship("User", foreign_keys=[student_id])
    owner = db.relationship("User", foreign_keys=[owner_id])

    messages = db.relationship("ChatMessage", backref="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("student_id", "owner_id", name="uniq_student_owner"),
    )
