from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from app import db
from ..models.admin import Admin
from ..models.user import User
from ..models.apartment import Apartment
from ..models.favorite import Favorite
import datetime
import jwt
from flask import current_app as app
from functools import wraps
import uuid as uuid_lib

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

# =========================
# helper - validate UUID
# =========================
def is_valid_uuid(val):
    try:
        uuid_lib.UUID(str(val))
        return True
    except ValueError:
        return False

# =========================
# ديكوريتور للتحقق من توكن الأدمن
# =========================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        if token.startswith("Bearer "):
            token = token[7:]  # إزالة "Bearer " من البداية
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_admin = Admin.query.get(data["admin_id"])
            if not current_admin:
                return jsonify({"error": "Invalid token"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(current_admin, *args, **kwargs)
    return decorated

# =========================
# تسجيل الدخول
# =========================
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

    return jsonify({
        "message": "Login successful",
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "email": admin.email
        },
        "token": token
    }), 200

# =========================
# إدارة الإدمنز
# =========================
@admin_bp.route("/", methods=["GET"])
@token_required
def get_admins(current_admin):
    admins = Admin.query.all()
    return jsonify([
        {"id": a.id, "username": a.username, "email": a.email, "created_at": a.created_at}
        for a in admins
    ]), 200

@admin_bp.route("/<string:admin_id>", methods=["DELETE"])
@token_required
def delete_admin(current_admin, admin_id):
    if not is_valid_uuid(admin_id):
        return jsonify({"error": "Invalid UUID"}), 400

    admin = Admin.query.get(admin_id)
    if not admin:
        return jsonify({"error": "Admin not found"}), 404

    db.session.delete(admin)
    db.session.commit()
    return jsonify({"message": "Admin deleted successfully"}), 200

# =========================
# إدارة المستخدمين
# =========================
@admin_bp.route("/users", methods=["GET"])
@token_required
def get_users(current_admin):
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "uuid": u.uuid,
            "name": u.full_name,
            "email": u.email,
            "role": u.role
        }
        for u in users
    ]), 200

@admin_bp.route("/users/<string:user_uuid>", methods=["DELETE"])
@token_required
def delete_user(current_admin, user_uuid):
    if not is_valid_uuid(user_uuid):
        return {"error": "Invalid UUID"}, 400

    # فلترة بالـ uuid مش id
    user = User.query.filter_by(uuid=user_uuid).first()
    if not user:
        return {"error": "User not found"}, 404

    if user.role == "owner":
        apartments = Apartment.query.filter_by(owner_id=user.id).all()
        for apt in apartments:
            Favorite.query.filter_by(apartment_id=apt.id).delete()
            db.session.delete(apt)

    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted successfully"}, 200


# =========================
# إدارة الشقق
# =========================
@admin_bp.route("/apartments", methods=["GET"])
@token_required
def get_apartments(current_admin):
    apartments = Apartment.query.all()
    return jsonify([
        {
            "id": a.id,
            "title": a.title,
            "address": a.address,
            "price": a.price
        }
        for a in apartments
    ]), 200

@admin_bp.route("/apartments/<string:id>", methods=["DELETE"])
@token_required
def delete_apartment(current_admin, id):
    if not is_valid_uuid(id):
        return jsonify({"error": "Invalid UUID"}), 400

    apartment = Apartment.query.get(id)
    if not apartment:
        return jsonify({"error": "Apartment not found"}), 404

    try:
        Favorite.query.filter_by(apartment_id=id).delete(synchronize_session=False)
        # هنا ممكن تضيف حذف Reviews و Images
        db.session.delete(apartment)
        db.session.commit()
        return {"message": "تم حذف الشقة بنجاح"}, 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# =========================
# الإحصائيات
# =========================
@admin_bp.route("/stats", methods=["GET"])
@token_required
def get_stats(current_admin):
    total_users = User.query.count()
    total_students = User.query.filter_by(role="student").count()
    total_owners = User.query.filter_by(role="owner").count()
    total_apartments = Apartment.query.count()

    return jsonify({
        "total_users": total_users,
        "total_students": total_students,
        "total_owners": total_owners,
        "total_apartments": total_apartments
    }), 200
