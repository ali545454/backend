import os
from datetime import timedelta
import cloudinary

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # DATABASE_URL مطلوب من متغيرات البيئة، افتراضي للتطوير
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    # تعديل الرابط عشان SQLAlchemy
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

    # تعطيل SSL لو مش مستخدم
    if "?" not in DATABASE_URL:
        DATABASE_URL += "?ssl=false"
    else:
        DATABASE_URL += "&ssl=false"

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"ssl": None}}

    # JWT_SECRET_KEY مطلوب من متغيرات البيئة، افتراضي للتطوير
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_COOKIE_CSRF_PROTECT = (
        os.getenv("JWT_COOKIE_CSRF_PROTECT", "true").lower() == "true"
    )
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


# ضبط cloudinary باستخدام متغيرات البيئة
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dev-cloud-name"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "dev-api-key"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "dev-api-secret"),
    secure=True,
)
