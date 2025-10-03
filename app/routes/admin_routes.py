from flask import Blueprint, request, jsonify, current_app as app
from .. import db
from ..models.user import User
from ..models.apartment import Apartment
from ..models.review import Review
from ..models.favorite import Favorite
from ..models.neighborhood import Neighborhood
from ..models.admin import Admin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, datetime, uuid
from functools import wraps

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

# =========================
# Helper: Require Admin JWT
# =========================
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token missing"}), 401
        try:
            token = token.split(" ")[1]  # Bearer <token>
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            if "admin_id" not in data:
                return jsonify({"error": "Not an admin token"}), 403
            admin = Admin.query.get(data["admin_id"])
            if not admin:
                return jsonify({"error": "Invalid token"}), 401
        except Exception:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(*args, **kwargs)
    return wrapper

# =========================
# Admin Auth
# =========================
@admin_bp.route("/register", methods=["POST"])
def register_admin():
    data = request.get_json()
    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "البيانات ناقصة"}), 400

    if Admin.query.filter((Admin.username == data["username"]) | (Admin.email == data["email"])).first():
        return jsonify({"error": "الأدمن موجود بالفعل"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_admin = Admin(
        id=str(uuid.uuid4()),
        username=data["username"],
        email=data["email"],
        password=hashed_password
    )
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({"message": "تم إنشاء الأدمن بنجاح"}), 201


@admin_bp.route("/login", methods=["POST"])
def login_admin():
    data = request.json
    admin = Admin.query.filter_by(email=data.get("email")).first()
    if not admin or not check_password_hash(admin.password, data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode(
        {
            "admin_id": admin.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        },
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    response = jsonify({
        "message": "Login successful",
        "admin": {"id": admin.id, "username": admin.username, "email": admin.email},
        "token": token
    })
    # إذا تحب تخزن الكوكيز:
    response.set_cookie("admin_token", token, httponly=True)
    return response

# =========================
# Stats
# =========================
@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    return jsonify({
        "users_count": User.query.count(),
        "apartments_count": Apartment.query.count(),
        "reviews_count": Review.query.count(),
        "favorites_count": Favorite.query.count(),
        "neighborhoods_count": Neighborhood.query.count(),
    })

# =========================
# Users
# =========================
@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@admin_bp.route("/users/<string:user_uuid>", methods=["DELETE"])
@admin_required
def delete_user(user_uuid):
    user = User.query.filter_by(uuid=user_uuid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})

# =========================
# Apartments
# =========================
@admin_bp.route("/apartments", methods=["GET"])
@admin_required
def get_apartments():
    apartments = Apartment.query.all()
    return jsonify([a.to_dict(include_all_images=True) for a in apartments])

@admin_bp.route("/apartments/<string:apartment_uuid>", methods=["DELETE"])
@admin_required
def delete_apartment(apartment_uuid):
    apartment = Apartment.query.filter_by(uuid=apartment_uuid).first()
    if not apartment:
        return jsonify({"error": "Apartment not found"}), 404
    db.session.delete(apartment)
    db.session.commit()
    return jsonify({"message": "Apartment deleted"})

# =========================
# Reviews
# =========================
@admin_bp.route("/reviews", methods=["GET"])
@admin_required
def get_reviews():
    reviews = Review.query.all()
    return jsonify([r.to_dict() for r in reviews])

@admin_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
@admin_required
def delete_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted"})

# =========================
# Neighborhoods
# =========================
@admin_bp.route("/neighborhoods", methods=["GET"])
@admin_required
def get_neighborhoods():
    neighborhoods = Neighborhood.query.all()
    return jsonify([n.to_dict() for n in neighborhoods])

@admin_bp.route("/neighborhoods", methods=["POST"])
@admin_required
def add_neighborhood():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400
    neighborhood = Neighborhood(name=data["name"])
    db.session.add(neighborhood)
    db.session.commit()
    return jsonify(neighborhood.to_dict()), 201

@admin_bp.route("/neighborhoods/<int:neighborhood_id>", methods=["DELETE"])
@admin_required
def delete_neighborhood(neighborhood_id):
    neighborhood = Neighborhood.query.get(neighborhood_id)
    if not neighborhood:
        return jsonify({"error": "Neighborhood not found"}), 404
    db.session.delete(neighborhood)
    db.session.commit()
    return jsonify({"message": "Neighborhood deleted"})
