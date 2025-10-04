from flask import Blueprint, request, jsonify
from .. import db 
from ..models import Apartment, Favorite, User
from flask_jwt_extended import jwt_required, get_jwt_identity

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/favorites/add', methods=['POST'])
@jwt_required(locations=["cookies"])
def add_to_favorites():
    data = request.get_json()
    apartment_uuid = data.get("apartment_id")  # ده UUID جاي من الفرونت
    user_uuid = get_jwt_identity()

    if not apartment_uuid:
        return jsonify({"message": "Apartment UUID is required"}), 400

    user = User.query.filter_by(uuid=user_uuid).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    apartment = Apartment.query.filter_by(uuid=apartment_uuid).first()
    if not apartment:
        return jsonify({"message": "Apartment not found"}), 404

    existing_favorite = Favorite.query.filter_by(
        user_id=user.id,
        apartment_id=apartment.id
    ).first()

    if existing_favorite:
        return jsonify({"message": "Apartment is already in favorites"}), 409

    try:
        new_favorite = Favorite(user_id=user.id, apartment_id=apartment.id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"message": "Apartment added to favorites successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
        
@favorites_bp.route('/favorites/remove/<string:apartment_uuid>', methods=['DELETE'])
@jwt_required(locations=["cookies"])
def remove_from_favorites(apartment_uuid):
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    apartment = Apartment.query.filter_by(uuid=apartment_uuid).first()
    if not apartment:
        return jsonify({"message": "Apartment not found"}), 404

    favorite_item = Favorite.query.filter_by(
        user_id=user.id,
        apartment_id=apartment.id  # 🟢 خد id العادي بعد ما تجيب الـ uuid
    ).first()

    if not favorite_item:
        return jsonify({"message": "Apartment not found in favorites"}), 404

    try:
        db.session.delete(favorite_item)
        db.session.commit()
        return jsonify({"message": "Apartment removed from favorites successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@favorites_bp.route("/favorites", methods=["GET"])
@jwt_required(locations=["cookies"])
def get_favorites():
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()
    if not user:
        return jsonify({"apartments": []}), 200

    # 🟢 جلب كل المفضلات الخاصة بالمستخدم
    favorites = Favorite.query.filter_by(user_id=user.id).all()
    fav_apartment_ids = [fav.apartment_id for fav in favorites]

    if not fav_apartment_ids:
        return jsonify({"apartments": []}), 200

    apartments_query = Apartment.query.filter(Apartment.id.in_(fav_apartment_ids)).all()

    apartments = []
    for apt in apartments_query:
        apartments.append({
            "uuid": apt.uuid,
            "title": apt.title,
            "price": apt.price,
            "address": apt.address,
            "rooms": apt.rooms,
            "main_image": apt.images[0].url if apt.images else None
        })

    return jsonify({"apartments": apartments}), 200

