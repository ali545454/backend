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

    # POST: create a new conversation.
    data = request.json or {}
    student_id = data.get("student_id")
    owner_id = data.get("owner_id")
    if not student_id or not owner_id:
        return jsonify({"error": "student_id and owner_id are required"}), 400
    conv = Conversation(
        student_id=student_id,
        owner_id=owner_id,
    )
    db.session.add(conv)
    db.session.commit()

    return jsonify({"id": conv.id, "student_id": conv.student_id, "owner_id": conv.owner_id}), 201


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


@messenger_bp.route("/messages/start", methods=["POST"])
def start_message_thread():
    # Creates a new conversation (if needed) then sends the first message.
    data = request.json or {}

    student_id = data.get("student_id")
    owner_id = data.get("owner_id")
    sender_id = data.get("sender_id")
    text = data.get("text")
    conversation_id = data.get("conversation_id")

    if conversation_id:
        conv = Conversation.query.get(conversation_id)
        if not conv:
            return jsonify({"error": "Conversation not found"}), 404
    else:
        if not student_id or not owner_id:
            return jsonify({"error": "student_id and owner_id are required if no conversation_id"}), 400
        conv = Conversation(
            student_id=student_id,
            owner_id=owner_id,
        )
        db.session.add(conv)
        db.session.commit()

    if not sender_id or not text:
        return jsonify({"error": "sender_id and text are required"}), 400

    msg = Message(
        conversation_id=conv.id,
        sender_id=sender_id,
        text=text,
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({
        "conversation_id": conv.id,
        "message_id": msg.id,
        "text": msg.text,
    }), 201
