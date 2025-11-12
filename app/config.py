import os
from datetime import timedelta
import cloudinary

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # -----------------------
    # ✅ إعدادات قاعدة البيانات
    # -----------------------
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # إصلاح URI لو كان جاي بدون 'mysql+pymysql://'
        if DATABASE_URL.startswith("mysql://"):
            DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
        
        # إضافة ?ssl=false لتجنب مشاكل SSL
        if "?" not in DATABASE_URL:
            DATABASE_URL += "?ssl=false"
        else:
            DATABASE_URL += "&ssl=false"

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------
    # ✅ إعدادات التشفير و JWT
    # -----------------------
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)

    # -----------------------
    # ✅ إعدادات رفع الصور
    # -----------------------
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ✅ Cloudinary config
cloudinary.config(secure=True)
