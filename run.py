import sys
import os    
from werkzeug.security import generate_password_hash

# --- الحل: إضافة مسار المشروع الرئيسي إلى نظام بايثون ---
# هذا السطر يضمن أن بايثون يمكنه العثور على مجلد 'app' وجميع مجلداته الفرعية
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# ---------------------------------------------------------

from app import create_app

app = create_app()

if __name__ == '__main__':
    # تم إضافة host='0.0.0.0' للسماح بالوصول من الأجهزة الأخرى على نفس الشبكة
    app.run(debug=True, host='0.0.0.0', port=5000)


