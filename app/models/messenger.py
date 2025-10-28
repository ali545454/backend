from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Conversation(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    is_group = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    members = db.relationship("ConversationMember", back_populates="conversation")
    messages = db.relationship("Message", back_populates="conversation")


class ConversationMember(db.Model):
    __tablename__ = "conversation_members"
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"))
    user_id = db.Column(db.Integer)  # ممكن تربطه بجدول users لو موجود
    joined_at = db.Column(db.DateTime, server_default=db.func.now())
    conversation = db.relationship("Conversation", back_populates="members")


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"))
    sender_id = db.Column(db.Integer)  # user_id المرسل
    text = db.Column(db.Text)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    conversation = db.relationship("Conversation", back_populates="messages")
