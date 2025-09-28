from flask import Blueprint, request, jsonify
from app import db
from ..models.apartment_view import ApartmentView
from ..models.apartment import Apartment
from flask_jwt_extended import jwt_required, get_jwt_identity

views_bp = Blueprint("views", __name__, url_prefix="/api/views")

@views_bp.route("/owner/details", methods=["GET"])
@jwt_required()  # تأكد أن المالك مسجل دخول
def owner_apartment_views():
    current_user_id = get_jwt_identity()  # ID المالك من التوكن

    # جلب كل الشقق الخاصة بالمالك
    apartments = Apartment.query.filter_by(owner_id=current_user_id).all()
    result = []

    for apartment in apartments:
        views_count = ApartmentView.query.filter_by(apartment_id=apartment.id).count()
        result.append({
            "apartment_id": apartment.id,
            "apartment_uuid": apartment.uuid,
            "title": apartment.title,
            "address": apartment.address,
            "price": apartment.price,
            "rooms": apartment.rooms,
            "views": views_count
        })

    return jsonify(result), 200
