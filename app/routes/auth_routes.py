from flask import Blueprint, request, jsonify, make_response
from app.models.user import User
from app import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import uuid as uuid_lib
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    full_name = data.get("fullName")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "البريد الإلكتروني مستخدم بالفعل"}), 400

    try:
        user = User(
            full_name=full_name,
            email=email,
            phone=data.get("phone"),
            birth_date=datetime.strptime(data.get("birthDate"), "%Y-%m-%d").date() if data.get("birthDate") else None,
            gender=data.get("gender"),
            role=data.get("userType", "student"),
            academic_year=data.get("academicYear"),
            college=data.get("faculty"),
            university=data.get("university"),
            uuid=str(uuid_lib.uuid4())
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # ✅ إنشاء Access Token
        access_token = create_access_token(identity=user.uuid)

        # ✅ نحطه في كوكي
        resp = make_response(jsonify({
            "message": "تم إنشاء الحساب وتسجيل الدخول",
            "user": user.to_dict()
        }), 201)

        resp.set_cookie(
            "access_token_cookie",
            access_token,
            httponly=True,
            secure=True,
            samesite="None"
        )



        return resp

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "حدث خطأ أثناء إنشاء الحساب", "details": str(e)}), 500
  
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # هوية JWT = UUID
    access_token = create_access_token(identity=user.uuid)

    # 🔑 نرجع الرد ومعاه الكوكي
    resp = make_response(jsonify({
        "message": "Logged in",
        "user": user.to_dict()
    }))
    resp.set_cookie(
        "access_token_cookie",
        access_token,
        httponly=True,
        secure=True,
        samesite="None"
    )

    return resp

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
@jwt_required(locations=["cookies"])
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