from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config
from flask_jwt_extended import JWTManager
from flask import send_from_directory
import os
import pymysql
pymysql.install_as_MySQLdb()
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # ✅ إعداد CORS (اسم الدومين الحقيقي بتاع الواجهة)
    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": ["https://yallasakn.vercel.app"]}}
    )

    # ✅ إعدادات JWT Cookies
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # غيّرها لمفتاح قوي
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"
    app.config["JWT_COOKIE_SECURE"] = True  # لازم True لأن الموقع HTTPS
    app.config["JWT_COOKIE_SAMESITE"] = "None"  # 👈 لازم None لما تتعامل من دومين مختلف
    app.config["JWT_COOKIE_HTTPONLY"] = True
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # مؤقتًا لغلق الـ CSRF لو لسه ما طبّقته

    # باقي الإعدادات
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    from . import models
    from .routes import register_routes
    register_routes(app)

    return app
