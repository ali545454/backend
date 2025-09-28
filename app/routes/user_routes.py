from flask import Blueprint, jsonify, request
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user_bp', __name__, url_prefix='/api/v1/user')


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()  # جلب ID من التوكن

    # حماية البيانات
    if current_user_id != user_id:
        return jsonify({"error": "غير مسموح بالوصول"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "fullName": user.full_name,
        "phone": user.phone,
        "avatar": f"{request.host_url.rstrip('/')}/uploads/default-avatar.png",
    }), 200
