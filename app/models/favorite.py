from .. import db

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    apartment = db.relationship('Apartment', back_populates='favorites')
    __table_args__ = (db.UniqueConstraint('user_id', 'apartment_id', name='unique_favorite'),)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "apartment_id": self.apartment_id
        }
