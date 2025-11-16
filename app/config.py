import os
from datetime import timedelta
import cloudinary

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # لو متغير البيئة DATABASE_URL مش موجود، نستخدم الرابط الخارجي لـ Railway
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql://root:XLbTyRplJTtLcOodYuRMpwTavDsSpHQn@switchyard.proxy.rlwy.net:25978/railway"
    )

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

    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)

    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ضبط cloudinary
cloudinary.config(secure=True)
