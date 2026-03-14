from flask import Blueprint, request, jsonify
from app import db
from ..models.apartment import Apartment
from ..models.apartment_view import ApartmentView
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from datetime import datetime, timedelta

views_bp = Blueprint("views", __name__, url_prefix="/api/views")


@views_bp.route("/track/<string:uuid>", methods=["POST"])
def track_view(uuid):
    apartment = Apartment.query.filter_by(uuid=uuid).first()
    if not apartment:
        return jsonify({"error": "Apartment not found"}), 404

    ip_address = request.remote_addr
    now = datetime.utcnow()
    spam_delay = now - timedelta(seconds=360)

    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        user_uuid = get_jwt_identity()
        if user_uuid:
            from app.models.user import User

            user = User.query.filter_by(uuid=user_uuid).first()
            user_id = user.id if user else None
    except Exception:
        user_id = None

    # تحقق من وجود مشاهدة سابقة
    if user_id:
        existing_view = ApartmentView.query.filter(
            ApartmentView.apartment_id == apartment.id,
            ApartmentView.user_id == user_id,  # أو حتى None لو مش مسجل
        ).first()
    else:
        existing_view = ApartmentView.query.filter(
            ApartmentView.apartment_id == apartment.id,
            ApartmentView.created_at >= spam_delay,
        ).first()

    if existing_view:
        return jsonify({"message": "View already recorded recently"}), 200

    # تسجيل المشاهدة
    view = ApartmentView(
        apartment_id=apartment.id,
        user_id=user_id,
        ip_address=ip_address,
        created_at=now,
    )
    db.session.add(view)
    db.session.commit()

    return jsonify({"message": "View recorded"}), 201
