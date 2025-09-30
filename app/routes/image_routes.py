from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
from app.models.apartment import Apartment
from app.models.image import Image  # جدول الصور
from app import db
import cloudinary.uploader

image_bp = Blueprint('image_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ✅ رفع صورة لشقة وربطها في قاعدة البيانات
@image_bp.route('/upload-image/<string:apartment_id>', methods=['POST'])
@jwt_required()
def upload_image(apartment_id):
    if 'image' not in request.files:
        return jsonify({'error': 'يجب اختيار ملف صورة'}), 400

    files = request.files.getlist("images")
    if file.filename == '':
        return jsonify({'error': 'اسم الملف فارغ'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'صيغة غير مدعومة'}), 400

    apartment = Apartment.query.filter_by(id=apartment_id).first()
    if not apartment:
        return jsonify({'error': 'الشقة غير موجودة'}), 404

    # ✅ رفع الصورة لـ Cloudinary
    try:
        result = cloudinary.uploader.upload(file)
        secure_url = result.get("secure_url")
    except Exception as e:
        return jsonify({'error': f'فشل في رفع الصورة: {str(e)}'}), 500

    # ✅ حفظ الرابط في جدول الصور وربطه بالشقة
    image = Image(url=secure_url, apartment_id=apartment.id)
    db.session.add(image)
    db.session.commit()

    return jsonify({
        'message': 'تم رفع الصورة بنجاح',
        'image_url': secure_url
    }), 201


# ✅ جلب كل صور شقة معينة
@image_bp.route('/apartment/<int:apartment_id>/images', methods=['GET'])
@cross_origin()
def get_apartment_images(apartment_id):
    images = Image.query.filter_by(apartment_id=apartment_id).all()

    if not images:
        return jsonify({'error': 'لا توجد صور لهذه الشقة'}), 404

    image_urls = [img.url for img in images]

    return jsonify({
        "apartment_id": apartment_id,
        "images": image_urls
    }), 200
