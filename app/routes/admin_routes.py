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

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

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

@admin_bp.route("/<int:admin_id>", methods=["DELETE"])
@token_required
def delete_admin(current_admin, admin_id):
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
            "name": u.full_name,
            "email": u.email,
            "role": u.role
        }
        for u in users
    ]), 200

@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@token_required
def delete_user(current_admin, user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    if user.role == "owner":
        apartments = Apartment.query.filter_by(owner_id=user_id).all()
        for apt in apartments:
            # حذف كل المفضلات المرتبطة بالشقة
            Favorite.query.filter_by(apartment_id=apt.id).delete()
            db.session.delete(apt)

    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted successfully"}

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

@admin_bp.route("/apartments/<int:id>", methods=["DELETE"])
@token_required
def delete_apartment(current_admin, id):
    apartment = Apartment.query.get_or_404(id)

    # حذف كل المفضلات المرتبطة بالشقة
    Favorite.query.filter_by(apartment_id=id).delete()

    db.session.delete(apartment)
    db.session.commit()
    return {"message": "تم حذف الشقة بنجاح"}

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
