from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.review import Review
from app.models.apartment import Apartment
from app.models.user import User
from app import db

review_bp = Blueprint('review_bp', __name__)

# ✅ إنشاء تقييم لشقة
@review_bp.route('/reviews/create', methods=['POST'])
@jwt_required()
def create_review():
    user_id = get_jwt_identity()
    data = request.get_json()

    apartment_id = data.get('apartment_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not apartment_id or not rating:
        return jsonify({'error': 'يجب توفير رقم الشقة والتقييم'}), 400

    if not (1 <= int(rating) <= 5):
        return jsonify({'error': 'التقييم يجب أن يكون بين 1 و 5'}), 400

    # تحقق من وجود الشقة
    apartment = Apartment.query.get(apartment_id)
    if not apartment:
        return jsonify({'error': 'الشقة غير موجودة'}), 404

    # تحقق إن المستخدم لم يقيم هذه الشقة من قبل
    existing = Review.query.filter_by(user_id=user_id, apartment_id=apartment_id).first()
    if existing:
        return jsonify({'error': 'لقد قمت بتقييم هذه الشقة من قبل'}), 400

    review = Review(
        user_id=user_id,
        apartment_id=apartment_id,
        rating=rating,
        comment=comment
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({'message': 'تم إضافة التقييم بنجاح', 'review': review.to_dict()}), 201


# ✅ جلب كل التقييمات لشقة
@review_bp.route('/reviews/apartment/<int:apartment_id>', methods=['GET'])
def get_reviews_for_apartment(apartment_id):
    apartment = Apartment.query.get(apartment_id)
    if not apartment:
        return jsonify({'error': 'الشقة غير موجودة'}), 404

    reviews = Review.query.filter_by(apartment_id=apartment_id).all()
    return jsonify([r.to_dict() for r in reviews]), 200


# ✅ حذف تقييم
@review_bp.route('/reviews/<int:review_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)

    if not review:
        return jsonify({'error': 'التقييم غير موجود'}), 404

    if review.user_id != user_id:
        return jsonify({'error': 'غير مصرح لك بحذف هذا التقييم'}), 403

    db.session.delete(review)
    db.session.commit()

    return jsonify({'message': 'تم حذف التقييم بنجاح'}), 200
# ✅ تعديل تقييم
@review_bp.route('/reviews/<int:review_id>/update', methods=['PATCH'])
@jwt_required()
def update_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)

    if not review:
        return jsonify({'error': 'التقييم غير موجود'}), 404

    if review.user_id != user_id:
        return jsonify({'error': 'غير مصرح لك بتعديل هذا التقييم'}), 403

    data = request.get_json()
    rating = data.get('rating', review.rating)
    comment = data.get('comment', review.comment)

    if not (1 <= int(rating) <= 5):
        return jsonify({'error': 'التقييم يجب أن يكون بين 1 و 5'}), 400

    review.rating = rating
    review.comment = comment
    db.session.commit()

    return jsonify({'message': 'تم تعديل التقييم بنجاح', 'review': review.to_dict()}), 200
# ✅ جلب كل التقييمات للمستخدم
@review_bp.route('/reviews/user', methods=['GET']) 
@jwt_required()
def get_user_reviews():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'المستخدم غير موجود'}), 404

    reviews = Review.query.filter_by(user_id=user_id).all()
    return jsonify([r.to_dict() for r in reviews]), 200