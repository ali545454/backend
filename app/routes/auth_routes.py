from flask import Blueprint, request, jsonify, make_response, current_app
from app.models.user import User
from app import db
from flask_jwt_extended import create_access_token, unset_jwt_cookies, set_access_cookies
import uuid as uuid_lib
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import re
import bleach
import logging

# Rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

auth_bp = Blueprint('auth_bp', __name__)
logger = logging.getLogger(__name__)

# NOTE: initialize Limiter in create_app and import it instead if you prefer app-global limiter.
limiter = Limiter(key_func=get_remote_address)

# -------------------- Helpers --------------------
def sanitize_str(s: str) -> str:
    if not s:
        return ""
    # Remove HTML/JS and strip tags
    return bleach.clean(s, tags=[], strip=True).strip()

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    # Basic regex; for stricter validation consider email_validator pkg
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))

def is_strong_password(pw: str) -> bool:
    if not pw or len(pw) < 8:
        return False
    checks = [
        bool(re.search(r'[a-z]', pw)),
        bool(re.search(r'[A-Z]', pw)),
        bool(re.search(r'[0-9]', pw)),
        bool(re.search(r'[^A-Za-z0-9]', pw))
    ]
    return sum(checks) >= 3

def clean_payload(payload: dict) -> dict:
    """Remove empty fields and sanitize strings"""
    out = {}
    for k, v in payload.items():
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        if isinstance(v, str):
            out[k] = sanitize_str(v)
        else:
            out[k] = v
    return out

# -------------------- Routes --------------------

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")  # rate-limit registration per IP
def register():
    try:
        data = request.get_json() or {}

        # server-side required fields validation
        full_name = (data.get("fullName") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not full_name or not email or not password:
            return jsonify({"error": "يرجى إدخال الحقول المطلوبة"}), 400

        if not is_valid_email(email):
            return jsonify({"error": "صيغة البريد الإلكتروني غير صحيحة"}), 400

        if not is_strong_password(password):
            return jsonify({"error": "كلمة المرور ضعيفة. استخدم 8+ أحرف وتضمّن أرقام/حروف كبيرة/رموز"}), 400

        # Prevent user enumeration: respond with generic error if exists
        if User.query.filter_by(email=email).first():
            # small delay could be added here (time.sleep) to reduce timing attacks
            return jsonify({"error": "لا يمكن إكمال الطلب"}), 400

        # sanitize optional fields and parse date
        phone = sanitize_str(data.get("phone") or "")
        birth_date = None
        if data.get("birthDate"):
            try:
                birth_date = datetime.strptime(data.get("birthDate"), "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "صيغة تاريخ الميلاد غير صحيحة"}), 400

        gender = sanitize_str(data.get("gender") or "")
        role = sanitize_str(data.get("userType") or "student")
        academic_year = sanitize_str(data.get("academicYear") or "")
        faculty = sanitize_str(data.get("faculty") or "")
        university = sanitize_str(data.get("university") or "")

        # create user
        user = User(
            full_name=sanitize_str(full_name),
            email=email,
            phone=phone or None,
            birth_date=birth_date,
            gender=gender or None,
            role=role,
            academic_year=academic_year or None,
            college=faculty or None,
            university=university or None,
            uuid=str(uuid_lib.uuid4())
        )
        # ensure set_password uses a secure hash (bcrypt)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # create access token with expiry
        expires = timedelta(hours=4)
        token = create_access_token(identity=user.uuid, expires_delta=expires)

        resp = make_response(jsonify({
            "message": "تم إنشاء الحساب وتسجيل الدخول",
            # DO NOT include sensitive fields here (e.g., password hash)
            "user": user.to_dict()
        }), 201)

        # set cookie using library helper (respects app config)
        set_access_cookies(resp, token)

        return resp

    except Exception:
        db.session.rollback()
        logger.exception("Register error")
        # do not leak internal error details to client
        return jsonify({"error": "حدث خطأ أثناء إنشاء الحساب"}), 500


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")  # rate-limit login attempts
def login():
    try:
        data = request.get_json() or {}
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify({"error": "يرجى إدخال البريد الإلكتروني وكلمة المرور"}), 400

        user = User.query.filter_by(email=email).first()
        # safe check: generic error message to avoid enumeration
        if not user or not user.check_password(password):
            # optional: add logging for failed attempts
            logger.info("Failed login attempt for email: %s", email)
            return jsonify({"error": "بيانات الدخول غير صحيحة"}), 401

        expires = timedelta(hours=4)
        token = create_access_token(identity=user.uuid, expires_delta=expires)

        resp = make_response(jsonify({
            "message": "تم تسجيل الدخول بنجاح",
            "user": user.to_dict()
        }))
        set_access_cookies(resp, token)
        return resp

    except Exception:
        logger.exception("Login error")
        return jsonify({"error": "حدث خطأ أثناء تسجيل الدخول"}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    # هذا الكود الآن سيعمل بشكل صحيح لأن الهوية هي uuid
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify(user.to_dict()), 200

@auth_bp.route('/update-password', methods=['POST'])
@jwt_required()
def update_password():
    # ✅ *** التعديل الثالث: البحث عن المستخدم باستخدام UUID ***
    user_uuid = get_jwt_identity() 
    data = request.get_json()

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'error': 'يرجى إدخال كلمة المرور القديمة والجديدة'}), 400

    # البحث باستخدام filter_by(uuid=...) بدلاً من .get()
    user = User.query.filter_by(uuid=user_uuid).first()

    if not user:
        return jsonify({'error': 'المستخدم غير موجود'}), 404

    if not check_password_hash(user.password_hash, old_password):
        return jsonify({'error': 'كلمة المرور القديمة غير صحيحة'}), 401

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'message': 'تم تحديث كلمة المرور بنجاح'}), 200

# ... (باقي الدوال مثل logout و update_profile تبقى كما هي لأنها صحيحة) ...



@auth_bp.route("/logout", methods=["POST"])
@jwt_required(optional=True, locations=["cookies"])
def logout():
    response = jsonify({"message": "تم تسجيل الخروج بنجاح"})
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route("/profile/update", methods=["PATCH"])
@jwt_required()
def update_profile():
    user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=user_uuid).first()

    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "No data provided"}), 400
    
    # ... (منطق التحديث يبقى كما هو) ...
    allowed_fields = ["full_name", "phone", "university", "college", "academic_year"]
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        resp = jsonify({"message": "تم تسجيل الخروج بنجاح"})
        resp.delete_cookie("token")
        return resp

@auth_bp.route("/check", methods=["GET"])
@jwt_required(locations=["cookies"])
def check_auth():
    return jsonify({"message": "Authenticated"}), 200