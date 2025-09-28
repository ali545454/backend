from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.neighborhood import Neighborhood
from app.models.user import User
from app import db

neighborhood_bp = Blueprint('neighborhood_bp', __name__)

# ✅ إنشاء حي جديد (للمشرف فقط)
@neighborhood_bp.route('/neighborhoods/create', methods=['POST'])
@jwt_required()
def create_neighborhood():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role != "مشرف":
        return jsonify({'error': 'غير مصرح لك'}), 403

    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'اسم الحي مطلوب'}), 400

    neighborhood = Neighborhood(name=name)
    db.session.add(neighborhood)
    db.session.commit()

    return jsonify({'message': 'تم إنشاء الحي بنجاح ✅', 'neighborhood': neighborhood.to_dict()}), 201


# ✅ جلب كل الأحياء
@neighborhood_bp.route('/neighborhoods', methods=['GET'])
def get_all_neighborhoods():
    neighborhoods = Neighborhood.query.all()
    return jsonify([n.to_dict() for n in neighborhoods]), 200


# ✅ حذف حي (للمشرف فقط)
@neighborhood_bp.route('/neighborhoods/<int:id>/delete', methods=['DELETE'])
@jwt_required()
def delete_neighborhood(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role != "مشرف":
        return jsonify({'error': 'غير مصرح لك'}), 403

    neighborhood = Neighborhood.query.get(id)
    if not neighborhood:
        return jsonify({'error': 'الحي غير موجود'}), 404

    db.session.delete(neighborhood)
    db.session.commit()
    return jsonify({'message': 'تم حذف الحي بنجاح'}), 200
