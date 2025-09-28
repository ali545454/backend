# routes/chat.py
from flask import Blueprint, request, jsonify
from ..models.chat_conversation import ChatConversation
from ..models.chat_message import ChatMessage
from ..models.user import User
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity

chat_bp = Blueprint("chat", __name__, url_prefix="/api/v1/chat")

# -------------------------
# 1️⃣ إنشاء محادثة جديدة
@chat_bp.route("/conversations", methods=["GET"])
@jwt_required()
def get_my_conversations():
    user_id = get_jwt_identity()

    # جلب المحادثات الخاصة بالطالب
    conversations = ChatConversation.query.filter_by(student_id=user_id).all()

    if not conversations:
        return jsonify({"conversations": []}), 200

    result = []
    for conv in conversations:
        owner = User.query.get(conv.owner_id)  # جلب بيانات المالك
        last_message = (
            ChatMessage.query.filter_by(conversation_id=conv.id)
            .order_by(ChatMessage.created_at.desc())
            .first()
        )

        result.append({
            "conversation_id": conv.id,
            "owner_id": conv.owner_id,
            "owner_name": owner.full_name if owner else "Unknown",
            "last_message": last_message.text if last_message else "",
            "last_message_at": last_message.created_at.strftime("%Y-%m-%d %H:%M:%S") if last_message else None
        })

    return jsonify({"conversations": result}), 200
 
# 2️⃣ إرسال رسالة داخل محادثة
@chat_bp.route("/conversation/<int:conversation_id>/messages/send", methods=["POST"])
@jwt_required()
def send_message(conversation_id):
    sender_id = get_jwt_identity()  # الطالب الحالي
    data = request.json
    text = data.get("text")

    if not text:
        return jsonify({"msg": "الرسالة مفقودة"}), 400

    message = ChatMessage(conversation_id=conversation_id, sender_id=sender_id, text=text)
    db.session.add(message)
    db.session.commit()

    return jsonify({
        "msg": "تم إرسال الرسالة",
        "message_id": message.id,
        "text": message.text,
        "sender_id": message.sender_id,
        "created_at": message.created_at.isoformat()
    }), 201

# -------------------------
# 3️⃣ جلب كل الرسائل لمحادثة
@chat_bp.route("/conversation/<int:conversation_id>/messages", methods=["GET"])
@jwt_required()
def get_conversation_messages(conversation_id):
    conversation = ChatConversation.query.get_or_404(conversation_id)
    messages = [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "text": m.text
        } for m in conversation.messages
    ]
    has_messages = len(messages) > 0  # <-- هذا التحقق من وجود رسائل
    return jsonify({
        "messages": messages,
        "has_messages": has_messages
    })


# -------------------------
# 4️⃣ تحديث رسالة كمقروءة
@chat_bp.route("/messages/<int:message_id>/read", methods=["PATCH"])
@jwt_required()
def mark_read(message_id):
    message = ChatMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    return jsonify({"msg": "تم تحديث الرسالة كمقروءة"})
@chat_bp.route("/conversation/check/<int:owner_id>", methods=["GET"])
@jwt_required()
def check_conversation(owner_id):
    student_id = get_jwt_identity()  # الطالب الحالي

    # جلب المحادثة لو موجودة
    conversation = ChatConversation.query.filter_by(student_id=student_id, owner_id=owner_id).first()
    if not conversation:
        return jsonify({"exists": False}), 200

    # جلب الرسائل مرتبة
    messages = sorted(conversation.messages, key=lambda m: m.created_at)

    messages = [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "text": m.text,
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for m in messages
    ]

    return jsonify({
        "exists": True,
        "conversation_id": conversation.id,
        "messages": messages
    }), 200
@chat_bp.route("/conversation/all", methods=["GET"])
@jwt_required()
def get_all_conversations():
    current_user_id = get_jwt_identity()

    conversations = ChatConversation.query.filter_by(student_id=current_user_id).all()

    data = []
    for conv in conversations:
        owner = conv.owner  # العلاقة مع User (المالك)
        last_message = conv.messages[-1] if conv.messages else None

        data.append({
            "conversation_id": conv.id,
            "owner_id": owner.id if owner else None,
            "owner_name": owner.full_name if owner else None,
            "owner_phone": owner.phone if owner else None,
            "owner_avatar": f"{request.host_url.rstrip('/')}/uploads/default-avatar.png",
            "last_message": {
                "text": last_message.text if last_message else None,
                "created_at": last_message.created_at.strftime("%Y-%m-%d %H:%M:%S") if last_message else None
            }
        })

    return jsonify(data), 200

