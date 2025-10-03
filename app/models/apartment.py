from flask import request
from .. import db
import uuid
import os
from datetime import datetime

class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    # تفاصيل أساسية
    rooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    kitchens = db.Column(db.Integer, nullable=False)
    total_beds = db.Column(db.Integer, nullable=False)
    available_beds = db.Column(db.Integer, nullable=False)

     # نوع السكن (شقة كاملة، غرفة، استوديو، مشترك)
    residence_type = db.Column(db.String(50), nullable=False)

    # نوع الساكن المفضل (شباب، بنات، عائلات، الكل)
    preferred_tenant_type = db.Column(db.String(50), nullable=True)


    # بيانات التواصل
    whatsapp_number = db.Column(db.String(20), nullable=True)

    # التحقق
    is_verified = db.Column(db.Boolean, default=True)

    # خصائص إضافية
    area = db.Column(db.Float, nullable=True)
    floor_number = db.Column(db.Integer, nullable=True)

    # --- المميزات ---
    has_elevator = db.Column(db.Boolean, default=False)
    has_wifi = db.Column(db.Boolean, default=False)
    has_ac = db.Column(db.Boolean, default=False)
    has_balcony = db.Column(db.Boolean, default=False)
    has_washing_machine = db.Column(db.Boolean, default=False)  # غسالة
    has_oven = db.Column(db.Boolean, default=False)             # بوتجاز/فرن
    has_gas = db.Column(db.Boolean, default=False)              # غاز طبيعي
    near_transport = db.Column(db.Boolean, default=False)       # قريب من المواصلات

    # مدة الإيجار المفضلة
    # (ترم واحد، سنة دراسية، شهر، مرن)

    # ملاحظات المالك
  
    # (ممنوع التدخين، ممنوع الشغب والضوضاء، ممنوع إزعاج الجيران...)

    # تاريخ إضافة الشقة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- العلاقات ---
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', back_populates='apartments')

    neighborhood_id = db.Column(db.Integer, db.ForeignKey('neighborhood.id'), nullable=False)
    neighborhood = db.relationship('Neighborhood', back_populates='apartments')

    reviews = db.relationship('Review', back_populates='apartment', cascade="all, delete-orphan")
    images = db.relationship('Image', back_populates='apartment', cascade='all, delete-orphan', lazy='select')
    favorites = db.relationship('Favorite', back_populates='apartment', lazy=True   , cascade="all, delete-orphan")

    # --- الخصائص المحسوبة ---
    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def average_rating(self):
        if not self.reviews:
            return 0.0
        total = sum(r.rating for r in self.reviews if r.rating is not None)
        count = len(self.reviews)
        return round(total / count, 1) if count > 0 else 0.0

    # --- دالة التحويل لقاموس ---
    def to_dict(self, user_favorite_apartment_ids=None, include_all_images=False):
        base_url = request.host_url.rstrip('/')

        # قائمة المميزات
        features = []
        if self.has_wifi:
            features.append("واي فاي")
        if self.has_ac:
            features.append("تكييف")
        if self.has_balcony:
            features.append("بلكونة")
        if self.has_elevator:
            features.append("مصعد")
        if self.has_washing_machine:
            features.append("غسالة")
        if self.has_oven:
            features.append("بوتجاز/فرن")
        if self.has_gas:
            features.append("غاز طبيعي")
        if self.near_transport:
            features.append("قريب من المواصلات")

        data = {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'address': self.address,
            'price': self.price,
            'bedrooms': self.rooms,
            'bathrooms': self.bathrooms,
            'kitchens': self.kitchens,
            'totalBeds': self.total_beds,
            'availableBeds': self.available_beds,
            'residenceType': self.residence_type,
            'whatsappNumber': self.whatsapp_number,
            'isVerified': self.is_verified,
            'ownerName': self.owner.full_name if self.owner else "مالك غير معروف",
            'neighborhood': self.neighborhood.name if self.neighborhood else "منطقة غير محددة",
            'area': self.area,
            'preferred_tenant_type': self.preferred_tenant_type,
            'floorNumber': self.floor_number,
            'features': features,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'rating': self.average_rating,
            'reviewCount': self.review_count,
            'isFavorite': self.id in (user_favorite_apartment_ids or []),
        }

        if include_all_images:
            data['images'] = [img.url for img in (self.images or [])]
        else:
            first_image = self.images[0] if self.images else None
            data['main_image'] = first_image.url if first_image else None


        return data
