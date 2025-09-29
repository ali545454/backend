from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config
from flask_jwt_extended import JWTManager
from flask import send_from_directory
import os
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    CORS(
        app,
        supports_credentials=True,
        resources={r"*": {"origins": "https://yallasakn.vercel.app"}}
    )





    app.config.from_object('app.config.Config')

    # ✅ إعدادات JWT عشان يقرأ من الكوكي
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # غيرها لمفتاح قوي
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]     # نقرأ التوكن من الكوكي
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"  # اسم الكوكي
    app.config["JWT_COOKIE_SECURE"] = True            # خليه True في HTTPS
    app.config["JWT_COOKIE_SAMESITE"] = "None"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
     # وقف CSRF Tokens مؤقتًا

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


    # تأكد من وجود مجلد الرفع
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # راوت لخدمة الصور
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    from . import models
    from .routes import register_routes
    register_routes(app)

    return app
