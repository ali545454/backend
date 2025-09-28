from flask import Blueprint, request, jsonify
from .. import db 
from ..models import Apartment, Favorite, User
from flask_jwt_extended import jwt_required, get_jwt_identity

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/add', methods=['POST'])
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
@favorites_bp.route('/remove/<string:apartment_uuid>', methods=['DELETE'])
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

    favorites = Favorite.query.filter_by(user_id=user.id).all()
    apartments = []
    for fav in favorites:
        apartment = Apartment.query.filter_by(id=fav.apartment_id).first()
        if apartment:
            apartments.append({
                "id": apartment.uuid,  # ✅ رجع UUID مش id
                "title": apartment.title,
                "price": apartment.price,
                "address": apartment.address,
                "rooms": apartment.rooms,
            })

    return jsonify({"apartments": apartments}), 200
