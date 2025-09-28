# app/models/user.py
from .. import db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
favorites = db.relationship('Favorite', backref='user', lazy=True)
from datetime import datetime
import uuid
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="student")
    password_hash = db.Column(db.String(128), nullable=False)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    academic_year = db.Column(db.String(50), nullable=True)
    college = db.Column(db.String(255), nullable=True)
    university = db.Column(db.String(255), nullable=True)

    # --- العلاقات ---
    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade="all, delete-orphan")
    
    # ✅ (التصحيح رقم 1) إضافة علاقة الشقق التي يملكها المستخدم
    # في كلاس User
    apartments = db.relationship('Apartment', back_populates='owner')


    # ✅ (التصحيح رقم 2) إضافة خاصية is_admin
    @property
    def is_admin(self):
        # هذه الخاصية سترجع True إذا كان دور المستخدم هو 'admin' أو 'مشرف'
        # عدّل القيمة لتطابق ما تستخدمه في قاعدة البيانات
        return self.role.lower() in ['admin', 'مشرف']

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            # ✅ (التصحيح رقم 3) تحويل التاريخ إلى نص
            'avatar': getattr(self, 'avatar_url', None), 
            'joinDate': self.created_at.strftime('%Y-%m-%d') if self.created_at else None,
            'propertiesCount': len(self.apartments),
            'rating': getattr(self, 'rating', 4.9), # مثال
            'responseTime': getattr(self, 'response_time', 'خلال ساعة'),# مثال
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender,
            "role": self.role,
            "academic_year": self.academic_year,
            "college": self.college,
            "university": self.university,
            
            # الآن كل هذه الأسطر ستعمل بشكل صحيح
            "favorites": [favorite.to_dict() for favorite in self.favorites],
            "reviews": [review.to_dict() for review in self.reviews],
            "apartments": [apartment.to_dict() for apartment in self.apartments],
            
            # يمكنك إرسال العدد مباشرة لتسهيل الأمر على الـ Frontend
            "favorites_count": len(self.favorites),
            "reviews_count": len(self.reviews),
            "apartments_count": len(self.apartments),
            
            # سيتم استدعاء الخاصية is_admin التي عرفناها في الأعلى
            "is_admin": self.is_admin
            
        }