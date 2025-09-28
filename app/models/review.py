from .. import db
from datetime import datetime

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # من 1 إلى 5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # علاقات الربط
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)

    user = db.relationship('User', back_populates='reviews')
    apartment = db.relationship('Apartment', back_populates='reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'date': self.created_at.strftime('%Y-%m-%d') if self.created_at else None,
            # نفترض أن لديك علاقة مع كاتب المراجعة (user)
            'user': self.user.full_name if self.user else "مستخدم غير معروف",
            'avatar': getattr(self.user, 'avatar_url', None) if self.user else None
                }
