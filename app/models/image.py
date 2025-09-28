# app/models/image.py
from .. import db

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)

    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    apartment = db.relationship('Apartment', back_populates='images')

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "apartment_id": self.apartment_id
        }
