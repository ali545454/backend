import os

import cloudinary.uploader
from flask import Blueprint, current_app, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models.apartment import Apartment
from app.models.apartment_view import ApartmentView
from app.models.favorite import Favorite
from app.models.image import Image
from app.models.review import Review
from app.models.user import User
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload

apartment_bp = Blueprint("apartment_bp", __name__)


def str_to_bool(val):
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes", "on")


def parse_pagination_args(default_per_page=20, max_per_page=100):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", default_per_page, type=int)
    page = 1 if not page or page < 1 else page
    per_page = default_per_page if not per_page or per_page < 1 else per_page
    per_page = min(per_page, max_per_page)
    return page, per_page


def wants_pagination() -> bool:
    return request.args.get("paginate", "false").lower() in ("1", "true", "yes")


@apartment_bp.route("/create", methods=["POST"])
@jwt_required(locations=["cookies"])
def create_apartment():
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first_or_404()

    try:
        data = request.form

        # --- الحقول الرقمية ---
        price = float(data.get("price", 0))
        area = float(data.get("area")) if data.get("area") else None
        rooms = int(data.get("rooms", 1))
        bathrooms = int(data.get("bathrooms", 1))
        kitchens = int(data.get("kitchens", 1))
        total_beds = int(data.get("total_beds", 0))
        available_beds = int(data.get("available_beds", 0))
        floor_number = (
            int(data.get("floor_number")) if data.get("floor_number") else None
        )

        # --- الحقول من نوع checkbox ---
        has_elevator = str_to_bool(data.get("has_elevator"))
        has_wifi = str_to_bool(data.get("has_wifi"))
        has_ac = str_to_bool(data.get("has_ac"))
        has_balcony = str_to_bool(data.get("has_balcony"))
        has_washing_machine = str_to_bool(data.get("has_washing_machine"))
        has_oven = str_to_bool(data.get("has_oven"))
        has_gas = str_to_bool(data.get("has_gas"))
        near_transport = str_to_bool(data.get("near_transport"))

        # --- إنشاء الشقة ---
        new_apartment = Apartment(
            title=data.get("title"),
            description=data.get("description"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            address=data.get("address"),
            neighborhood_id=int(data.get("neighborhood_id")),
            owner_id=user.id,
            price=price,
            rooms=rooms,
            bathrooms=bathrooms,
            kitchens=kitchens,
            total_beds=total_beds,
            available_beds=available_beds,
            residence_type=data.get("residence_type"),
            preferred_tenant_type=data.get("preferred_tenant_type"),
            whatsapp_number=data.get("whatsapp_number"),
            area=area,
            floor_number=floor_number,
            has_elevator=has_elevator,
            has_wifi=has_wifi,
            has_ac=has_ac,
            has_balcony=has_balcony,
            has_washing_machine=has_washing_machine,
            has_oven=has_oven,
            has_gas=has_gas,
            near_transport=near_transport,
            is_verified=False,
        )

        db.session.add(new_apartment)
        db.session.flush()  # عشان نجيب ID قبل رفع الصور

        # --- رفع الصور على Cloudinary ---
        images = request.files.getlist("images")
        for img_file in images:
            upload_result = cloudinary.uploader.upload(
                img_file, folder=f"apartments/{new_apartment.id}"
            )
            new_image = Image(
                url=upload_result["secure_url"], apartment_id=new_apartment.id
            )
            db.session.add(new_image)

        db.session.commit()  # هنا نعمل commit مرة واحدة بعد كل التعديلات

        return (
            jsonify(
                {
                    "message": "Apartment created successfully",
                    "apartment_id": new_apartment.id,
                    "title": new_apartment.title,
                    "latitude": new_apartment.latitude,
                    "longitude": new_apartment.longitude,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
        return jsonify({"error": "حدث خطأ غير متوقع في الخادم"}), 500


@apartment_bp.route("/all_apartments", methods=["GET"])
@apartment_bp.route("/", methods=["GET"])
def get_all_apartments():
    user_id = getattr(g, "user_id", None)

    favorite_apartment_ids = []
    if user_id:
        user_favorites = Favorite.query.filter_by(user_id=user_id).all()
        favorite_apartment_ids = [fav.apartment_id for fav in user_favorites]

    base_query = Apartment.query.options(
        joinedload(Apartment.owner),
        joinedload(Apartment.neighborhood),
        selectinload(Apartment.images),
        selectinload(Apartment.reviews),
    ).order_by(Apartment.created_at.desc())

    if wants_pagination():
        page, per_page = parse_pagination_args(default_per_page=20, max_per_page=100)
        pagination = base_query.paginate(page=page, per_page=per_page, error_out=False)
        apartments_data = [
            ap.to_dict(
                user_favorite_apartment_ids=favorite_apartment_ids, include_all_images=True
            )
            for ap in pagination.items
        ]
        return (
            jsonify(
                {
                    "items": apartments_data,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": pagination.total,
                        "pages": pagination.pages,
                    },
                }
            ),
            200,
        )

    apartments = base_query.all()

    apartments_data = [
        ap.to_dict(
            user_favorite_apartment_ids=favorite_apartment_ids, include_all_images=True
        )
        for ap in apartments
    ]

    return jsonify(apartments_data), 200


# ✅ Update apartment
@apartment_bp.route("/apartments/<int:id>/update", methods=["PATCH"])
@apartment_bp.route("/<int:id>/update", methods=["PATCH"])
@jwt_required()
def update_apartment(id):
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    apartment = Apartment.query.get(id)

    if not apartment:
        return jsonify({"error": "Apartment not found"}), 404

    if apartment.owner_id != user.id:
        return (
            jsonify({"error": "You are not authorized to update this apartment"}),
            403,
        )

    data = request.get_json() or {}

    apartment.title = data.get("title", apartment.title)
    apartment.description = data.get("description", apartment.description)
    apartment.address = data.get("address", apartment.address)
    apartment.price = data.get("price", apartment.price)
    apartment.rooms = data.get("rooms", apartment.rooms)
    apartment.neighborhood_id = data.get("neighborhood_id", apartment.neighborhood_id)

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Apartment updated successfully",
                "apartment": apartment.to_dict(),
            }
        ),
        200,
    )


@apartment_bp.route("/apartments/<string:uuid>/delete", methods=["DELETE"])
@apartment_bp.route("/<string:uuid>/delete", methods=["DELETE"])
@jwt_required(locations=["cookies"])
def delete_apartment(uuid):
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    apartment = Apartment.query.filter_by(uuid=uuid).first()
    if not apartment:
        return jsonify({"error": "Apartment not found"}), 404

    if apartment.owner_id != user.id:
        return (
            jsonify({"error": "You are not authorized to delete this apartment"}),
            403,
        )

    # 🗑️ امسح المفضلات
    Favorite.query.filter_by(apartment_id=apartment.id).delete()

    # 🗑️ امسح المشاهدات
    ApartmentView.query.filter_by(apartment_id=apartment.id).delete()

    # 🗑️ امسح الصور
    for img in apartment.images:
        try:
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], img.url)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print("❌ Error deleting image:", e)
        db.session.delete(img)

    # 🗑️ امسح التقييمات (لو عندك reviews)
    Review.query.filter_by(apartment_id=apartment.id).delete()

    # 🗑️ امسح الشقة نفسها
    db.session.delete(apartment)
    db.session.commit()

    return jsonify({"message": "Apartment deleted successfully"}), 200


# ✅ Admin verify apartment
@apartment_bp.route("/admin/verify-apartment/<int:id>", methods=["PATCH"])
@jwt_required()
def verify_apartment(id):
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()

    if not user or user.role != "admin":
        return jsonify({"error": "You are not authorized"}), 403

    apartment = Apartment.query.get(id)
    if not apartment:
        return jsonify({"error": "Apartment not found"}), 404

    apartment.is_verified = True
    db.session.commit()

    return jsonify({"message": "Apartment verified successfully ✅"}), 200


# ✅ Get all verified apartments
@apartment_bp.route("/apartments/verified", methods=["GET"])
@apartment_bp.route("/verified", methods=["GET"])
def get_verified_apartments():
    apartments = (
        Apartment.query.options(
            joinedload(Apartment.owner),
            joinedload(Apartment.neighborhood),
            selectinload(Apartment.images),
            selectinload(Apartment.reviews),
        )
        .filter_by(is_verified=True)
        .all()
    )
    return jsonify([ap.to_dict() for ap in apartments]), 200


# ✅ Get apartments of current owner + stats
@apartment_bp.route("/my-apartments", methods=["GET"])
@jwt_required(locations=["cookies"])
def get_my_apartments():
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # ✅ كل شقق المالك
    apartments = (
        Apartment.query.options(
            joinedload(Apartment.neighborhood),
            selectinload(Apartment.images),
        )
        .filter_by(owner_id=user.id)
        .all()
    )

    # ✅ لو مفيش شقق
    if not apartments:
        return (
            jsonify(
                {
                    "stats": {
                        "total_apartments": 0,
                        "total_views": 0,
                        "apartments_per_month": {},
                    },
                    "apartments": [],
                }
            ),
            200,
        )

    # ---------- 🏠 بيانات الشقق ----------
    result = []
    apartments_per_month = {}

    apartment_ids = [apt.id for apt in apartments]
    views_rows = (
        db.session.query(
            ApartmentView.apartment_id,
            func.count(ApartmentView.id).label("views_count"),
        )
        .filter(ApartmentView.apartment_id.in_(apartment_ids))
        .group_by(ApartmentView.apartment_id)
        .all()
    )
    views_map = {row.apartment_id: row.views_count for row in views_rows}

    for apt in apartments:
        main_image = apt.images[0] if apt.images else None
        views_count = views_map.get(apt.id, 0)

        # 📅 حساب عدد الشقق في كل شهر بناءً على created_at
        if hasattr(apt, "created_at") and apt.created_at:
            month_name = apt.created_at.strftime("%B %Y")  # مثال: "August 2025"
            apartments_per_month[month_name] = (
                apartments_per_month.get(month_name, 0) + 1
            )

        result.append(
            {
                "uuid": apt.uuid,
                "id": apt.id,
                "title": apt.title,
                "price": apt.price,
                "neighborhood": apt.neighborhood.name if apt.neighborhood else None,
                "status": "متاحة",
                "main_image": main_image.url if main_image else None,
                "views": views_count,
            }
        )

    # ---------- 📊 الإحصائيات ----------
    stats = {
        "total_apartments": len(apartments),
        "total_views": sum(views_map.values()),
        "apartments_per_month": apartments_per_month,
    }

    return jsonify({"stats": stats, "apartments": result}), 200


# ✅ Filter apartments
@apartment_bp.route("/apartments/filter", methods=["GET"])
@apartment_bp.route("/filter", methods=["GET"])
def filter_apartments():
    neighborhood_id = request.args.get("neighborhood_id")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    rooms = request.args.get("rooms", type=int)

    query = Apartment.query.filter_by(is_verified=True)

    if neighborhood_id:
        query = query.filter_by(neighborhood_id=neighborhood_id)
    if min_price is not None:
        query = query.filter(Apartment.price >= min_price)
    if max_price is not None:
        query = query.filter(Apartment.price <= max_price)
    if rooms:
        query = query.filter_by(rooms=rooms)

    apartments = query.options(
        joinedload(Apartment.owner),
        joinedload(Apartment.neighborhood),
        selectinload(Apartment.images),
        selectinload(Apartment.reviews),
    ).all()
    return jsonify([ap.to_dict() for ap in apartments]), 200


# ✅ Search apartments by title
@apartment_bp.route("/apartments/search", methods=["GET"])
@apartment_bp.route("/search", methods=["GET"])
def search_apartments():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "Please enter a search term"}), 400

    apartments = (
        Apartment.query.options(
            joinedload(Apartment.owner),
            joinedload(Apartment.neighborhood),
            selectinload(Apartment.images),
            selectinload(Apartment.reviews),
        )
        .filter(Apartment.title.ilike(f"%{query}%"))
        .all()
    )
    return jsonify([ap.to_dict() for ap in apartments]), 200


# ✅ Get apartments of current owner
@apartment_bp.route("/owner-apartments", methods=["GET"])
@jwt_required(locations=["cookies"])
def get_owner_apartments():
    user_uuid = get_jwt_identity()  # هيرجع uuid

    # نجيب اليوزر من جدول users عن طريق uuid
    user = User.query.filter_by(uuid=user_uuid).first()
    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404

    # نستخدم user.id في البحث عن الشقق
    apartments = (
        Apartment.query.options(selectinload(Apartment.images))
        .filter_by(owner_id=user.id)
        .all()
    )

    # نحول النتائج إلى JSON
    result = []
    for apt in apartments:
        result.append(
            {
                "id": apt.id,
                "title": apt.title,
                "description": apt.description,
                "address": apt.address,
                "price": apt.price,
                "rooms": apt.rooms,
                "owner_id": apt.owner_id,
                "neighborhood_id": apt.neighborhood_id,
                "is_verified": apt.is_verified,
                "kitchens": apt.kitchens,
                "total_beds": apt.total_beds,
                "available_beds": apt.available_beds,
                "residence_type": apt.residence_type,
                "whatsapp_number": apt.whatsapp_number,
                "bathrooms": apt.bathrooms,
                "images": [
                    f"{request.host_url}uploads/{img.url}" for img in apt.images
                ],
            }
        )

    return jsonify({"apartments": result}), 200


@apartment_bp.route("/apartments/<int:id>", methods=["GET"])
@apartment_bp.route("/<int:id>", methods=["GET"])
def get_apartment_by_id(id):
    apartment = (
        Apartment.query.options(
            joinedload(Apartment.owner),
            joinedload(Apartment.neighborhood),
            selectinload(Apartment.images),
            selectinload(Apartment.reviews),
        )
        .filter_by(id=id)
        .first_or_404()
    )
    return jsonify(apartment.to_dict()), 200


@apartment_bp.route("/apartment/<string:uuid>/reviews", methods=["POST"])
@apartment_bp.route("/<string:uuid>/reviews", methods=["POST"])
@jwt_required(locations=["cookies"])
def add_review_to_apartment(uuid):
    # 1. الحصول على هوية المستخدم من التوكن
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first_or_404()

    # 2. التأكد من وجود الشقة
    apartment = (
        Apartment.query.options(
            joinedload(Apartment.owner),
            joinedload(Apartment.neighborhood),
            selectinload(Apartment.images),
            selectinload(Apartment.reviews),
        )
        .filter_by(uuid=uuid)
        .first_or_404()
    )

    # 3. قراءة البيانات من الطلب (request)
    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    rating = data.get("rating")
    comment = data.get("comment")

    # 4. التحقق من صحة البيانات
    if not rating:
        return jsonify({"error": "Rating is required"}), 400

    try:
        rating_int = int(rating)
        if not 1 <= rating_int <= 5:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400

    # يمكنك إضافة منطق لمنع المستخدم من إضافة أكثر من مراجعة لنفس الشقة
    existing_review = Review.query.filter_by(
        user_id=user.id, apartment_id=apartment.id
    ).first()
    if existing_review:
        return (
            jsonify({"error": "You have already reviewed this apartment"}),
            409,
        )  # 409 Conflict

    # 5. إنشاء المراجعة الجديدة وحفظها
    try:
        new_review = Review(
            rating=rating_int,
            comment=comment,
            user_id=user.id,
            apartment_id=apartment.id,
        )
        db.session.add(new_review)
        db.session.commit()

        # 6. إرجاع رسالة نجاح مع بيانات المراجعة الجديدة
        return (
            jsonify(
                {"message": "Review added successfully", "review": new_review.to_dict()}
            ),
            201,
        )  # 201 Created

    except Exception as e:
        db.session.rollback()
        print(f"Error adding review: {e}")
        return jsonify({"error": "An internal error occurred"}), 500


@apartment_bp.route("/apartment/<string:uuid>", methods=["GET"])
@apartment_bp.route("/<string:uuid>", methods=["GET"])
@jwt_required(locations=["cookies"])
def get_apartment_details(uuid):
    get_jwt_identity()  # تأكد أن المستخدم مصادق عليه
    apartment = Apartment.query.filter_by(uuid=uuid).first_or_404()
    data = apartment.to_dict(include_all_images=True)

    if apartment.owner:
        data["owner"] = {
            "id": apartment.owner.id,
            "fullName": apartment.owner.full_name,
            "phone": apartment.owner.phone,
            "avatar": f"{request.host_url.rstrip('/')}/uploads/default-avatar.png",
            "initial": (
                apartment.owner.full_name[0] if apartment.owner.full_name else "م"
            ),
        }
    else:
        data["owner"] = None

    return jsonify(data), 200


# لو عندك موديل Apartment ومكتبة db = SQLAlchemy()


@apartment_bp.route("/featured", methods=["GET"])
def get_featured_apartments():
    apartments = (
        Apartment.query.options(
            joinedload(Apartment.neighborhood),
            selectinload(Apartment.images),
            selectinload(Apartment.reviews),
            joinedload(Apartment.owner),
        )
        .order_by(Apartment.id.desc())
        .limit(3)
        .all()
    )

    result = []
    for apt in apartments:
        data = apt.to_dict(include_all_images=True)  # ✅ نفس اللوجيك بتاع التفاصيل

        # الحي
        if apt.neighborhood:
            data["neighborhood"] = {
                "id": apt.neighborhood.id,
                "name": apt.neighborhood.name,
            }
        else:
            data["neighborhood"] = None

        # لو عايز بس صورة واحدة (أول صورة مثلاً)
        if data.get("images"):
            data["image"] = data["images"][0]
        else:
            data["image"] = None

        result.append(data)

    return jsonify(result), 200
