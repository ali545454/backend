# في ملف app/utils/auth_utils.py
from flask_jwt_extended import get_jwt_identity, jwt_required
from functools import wraps
from flask import g, request, jsonify


def login_required(f):
    @wraps(f)
    @jwt_required()  # هذا هو الديكوراتور الحقيقي من flask_jwt_extended
    def decorated_function(*args, **kwargs):
        # 1. احصل على مُعرف المستخدم من الرمز
        current_user_id = get_jwt_identity()

        # 2. قم بتخزينه في كائن g ليسهل الوصول إليه
        g.user_id = current_user_id

        return f(*args, **kwargs)

    return decorated_function


def validate_json(*required_fields):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json() or {}
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"الحقل {field} مطلوب"}), 400
            return f(*args, **kwargs)

        return decorated

    return decorator
