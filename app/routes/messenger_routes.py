from flask import Blueprint, request, jsonify
from app.models import db, Conversation, Message

# Blueprint is registered at /api/v1 (see app/routes/__init__.py).
# This lets us expose endpoints like /api/v1/chat/conversations and /api/v1/messages/start
messenger_bp = Blueprint("messenger", __name__, url_prefix="/api/v1")


def _serialize_conversation(conv: Conversation) -> dict:
    return {
        "id": conv.id,
        "student_id": conv.student_id,
        "owner_id": conv.owner_id,
        "created_at": conv.created_at.isoformat() if conv.created_at else None,
    }


@messenger_bp.route("/conversations", methods=["GET", "POST"])
@messenger_bp.route("/chat/conversations", methods=["GET", "POST"])
def conversations():
    if request.method == "GET":
        # return all conversations (for demo purposes)
        convs = Conversation.query.all()
        return jsonify([_serialize_conversation(c) for c in convs]), 200

    # POST: find or create a new conversation.
    data = request.json or {}
    student_id = data.get("student_id")
    owner_id = data.get("owner_id")
    if not student_id or not owner_id:
        return jsonify({"error": "student_id and owner_id are required"}), 400
    
    # Check if conversation already exists
    conv = Conversation.query.filter_by(student_id=student_id, owner_id=owner_id).first()
    if conv:
        return jsonify(_serialize_conversation(conv)), 200
    
    # Create new conversation
    conv = Conversation(
        student_id=student_id,
        owner_id=owner_id,
    )
    db.session.add(conv)
    db.session.commit()

    return jsonify(_serialize_conversation(conv)), 201


@messenger_bp.route("/messages/start", methods=["POST"])
def start_conversation():
    data = request.json or {}
    student_id = data.get("student_id")
    owner_id = data.get("owner_id")
    text = data.get("text")
    if not student_id or not owner_id or not text:
        return jsonify({"error": "student_id, owner_id, and text are required"}), 400
    
    # Find or create conversation
    conv = Conversation.query.filter_by(student_id=student_id, owner_id=owner_id).first()
    if not conv:
        conv = Conversation(student_id=student_id, owner_id=owner_id)
        db.session.add(conv)
        db.session.commit()
    
    # Send the first message
    msg = Message(
        conversation_id=conv.id,
        sender_id=student_id,  # Assuming student starts the conversation
        text=text,
    )
    db.session.add(msg)
    db.session.commit()
    
    return jsonify({
        "conversation": _serialize_conversation(conv),
        "message": {
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "sender_id": msg.sender_id,
            "text": msg.text,
            "is_read": msg.is_read,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        }
    }), 201


@messenger_bp.route("/messages", methods=["POST"])
@messenger_bp.route("/chat/messages", methods=["POST"])
def send_message():
    data = request.json or {}
    conversation_id = data.get("conversation_id")
    sender_id = data.get("sender_id")
    text = data.get("text")
    if not conversation_id or not sender_id or not text:
        return jsonify({"error": "conversation_id, sender_id, and text are required"}), 400
    msg = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        text=text,
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"id": msg.id, "text": msg.text}), 201


@messenger_bp.route("/messages/<int:conversation_id>", methods=["GET"])
def get_messages(conversation_id):
    # Get all messages for a specific conversation
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
    return jsonify([{
        "id": msg.id,
        "conversation_id": msg.conversation_id,
        "sender_id": msg.sender_id,
        "text": msg.text,
        "is_read": msg.is_read,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
    } for msg in messages]), 200


@messenger_bp.route("/messages/<int:message_id>/read", methods=["PUT"])
def mark_message_read(message_id):
    # Mark a message as read
    msg = Message.query.get(message_id)
    if not msg:
        return jsonify({"error": "Message not found"}), 404
    msg.is_read = True
    db.session.commit()
    return jsonify({"id": msg.id, "is_read": msg.is_read}), 200
