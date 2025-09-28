from .. import db

class Neighborhood(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    # العلاقة مع الشقق
    apartments = db.relationship('Apartment', back_populates='neighborhood')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

    # دالة لعرض الكائن بشكل مقروء
    def __repr__(self):
        return f"<Neighborhood {self.name}>"
