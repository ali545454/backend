from flask import Blueprint, request, jsonify
from .models import db, Conversation, ConversationMember, Message

messenger_bp = Blueprint("messenger", __name__, url_prefix="/messenger")


@messenger_bp.route("/conversations", methods=["POST"])
def create_conversation():
    data = request.json
    conv = Conversation(title=data.get("title"), is_group=data.get("is_group", False))
    db.session.add(conv)
    db.session.commit()
    # إضافة الأعضاء
    for user_id in data.get("members", []):
        member = ConversationMember(conversation_id=conv.id, user_id=user_id)
        db.session.add(member)
    db.session.commit()
    return jsonify({"id": conv.id, "title": conv.title}), 201


@messenger_bp.route("/messages", methods=["POST"])
def send_message():
    data = request.json
    msg = Message(
        conversation_id=data["conversation_id"],
        sender_id=data["sender_id"],
        text=data["text"],
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"id": msg.id, "text": msg.text}), 201
