import os
from datetime import timedelta
import cloudinary

# المسار الأساسي للمشروع
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # إعدادات قاعدة البيانات (MySQL)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # مفتاح التشفير
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")

    # إعدادات JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)

    # مسار حفظ الصور (لو عايز تحفظ نسخة محليًا)
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

    # السماح بأنواع معينة من الصور فقط
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ✅ Cloudinary config (يتنادى مرة واحدة بس)
cloudinary.config(
    secure=True
    # مش لازم تحدد الباقي، SDK هيقرأهم من CLOUDINARY_URL أو من
    # CLOUDINARY_CLOUD_NAME + CLOUDINARY_API_KEY + CLOUDINARY_API_SECRET
)
