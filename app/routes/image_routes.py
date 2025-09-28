from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models.apartment import Apartment
from app.models.image import Image  # جدول الصور
from app import db
import os
import uuid
from flask_cors import cross_origin

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

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'اسم الملف فارغ'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'صيغة غير مدعومة'}), 400

    apartment = Apartment.query.filter_by(id=apartment_id).first()
    if not apartment:
        return jsonify({'error': 'الشقة غير موجودة'}), 404

    # تغيير اسم الملف لتفادي التكرار
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    # حفظ الملف
    file.save(path)

    # حفظ اسم الملف في جدول الصور وربطه بالشقة
    image = Image(url=filename, apartment_id=apartment.id)

    db.session.add(image)
    db.session.commit()

    image_url = f"{request.host_url}uploads/{filename}"
    return jsonify({'message': 'تم رفع الصورة بنجاح', 'image_url': image_url}), 201

# ✅ عرض صورة
@image_bp.route('/uploads/<filename>', methods=['GET'])
def get_uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)




@image_bp.route('/apartment/<int:apartment_id>/images', methods=['GET'])
@cross_origin()
def get_apartment_images(apartment_id):
    images = Image.query.filter_by(apartment_id=apartment_id).all()

    if not images:
        return jsonify({'error': 'No images found for this apartment'}), 404

    base_url = request.host_url.rstrip('/')
    image_urls = [f"{base_url}/uploads/{img.url}" for img in images]

    return jsonify({
        "apartment_id": apartment_id,
        "images": image_urls
    }), 200
