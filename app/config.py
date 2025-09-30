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

    # Cloudinary configuration (أسهل كده)
    cloudinary.config(
        secure=True,
        cloud_name=None,  # مش محتاج تحطهم، SDK هيقراهم من CLOUDINARY_URL
        api_key=None,
        api_secret=None
    )
