import os
from datetime import timedelta

# المسار الأساسي للمشروع
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # إعدادات قاعدة البيانات (MySQL)
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:XLbTyRplJTtLcOodYuRMpwTavDsSpHQn@switchyard.proxy.rlwy.net:25978/railway"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # مفتاح التشفير
    SECRET_KEY = "your-secret-key"

    # إعدادات JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)

    # مسار حفظ الصور
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

    # السماح بأنواع معينة من الصور فقط (اختياري)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
   
    # JWT Cookies settings
