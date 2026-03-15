from flask import Blueprint, jsonify, request
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
import re
import bleach

user_bp = Blueprint("user_bp", __name__, url_prefix="/api/v1/user")


def sanitize_str(s: str) -> str:
    if not s:
        return ""
    return bleach.clean(s, tags=[], strip=True).strip()


@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required(locations=["cookies"])
def get_user(user_id):
    current_user_uuid = get_jwt_identity()
    current_user = User.query.filter_by(uuid=current_user_uuid).first()

    if not current_user:
        return jsonify({"error": "المستخدم الحالي غير موجود"}), 404

    # حماية البيانات
    if current_user.id != user_id:
        return jsonify({"error": "غير مسموح بالوصول"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return (
        jsonify(
            {
                "id": user.id,
                "fullName": user.full_name,
                "phone": user.phone,
                "avatar": f"{request.host_url.rstrip('/')}/uploads/default-avatar.png",
            }
        ),
        200,
    )


@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required(locations=["cookies"])
def update_user(user_id):
    current_user_uuid = get_jwt_identity()
    current_user = User.query.filter_by(uuid=current_user_uuid).first()

    if not current_user:
        return jsonify({"error": "المستخدم الحالي غير موجود"}), 404

    if current_user.id != user_id:
        return jsonify({"error": "غير مسموح بالوصول"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404

    data = request.get_json() or {}

    # Update fields if provided
    if "fullName" in data:
        user.full_name = sanitize_str(data["fullName"])
    if "phone" in data:
        new_phone = sanitize_str(data["phone"])
        if new_phone and User.query.filter(User.phone == new_phone, User.id != user_id).first():
            return jsonify({"error": "رقم الهاتف مستخدم بالفعل"}), 400
        user.phone = new_phone or None
    if "email" in data:
        new_email = sanitize_str(data["email"]).lower()
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", new_email):
            return jsonify({"error": "صيغة البريد الإلكتروني غير صحيحة"}), 400
        if User.query.filter(User.email == new_email, User.id != user_id).first():
            return jsonify({"error": "البريد الإلكتروني مستخدم بالفعل"}), 400
        user.email = new_email

    # Add more fields as needed

    db.session.commit()

    return jsonify({"message": "تم تحديث البيانات بنجاح", "user": user.to_dict()}), 200
