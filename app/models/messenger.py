from app import db


class Conversation(db.Model):
    __tablename__ = "chat_conversations"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    messages = db.relationship("Message", back_populates="conversation")


class Message(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("chat_conversations.id"))
    sender_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    conversation = db.relationship("Conversation", back_populates="messages")
