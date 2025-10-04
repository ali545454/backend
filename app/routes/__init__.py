from .auth_routes import auth_bp
from .apartment_routes import apartment_bp
from .reviews_routes import review_bp
from .user_routes import user_bp
from .favorite_routes import favorites_bp 
from .image_routes import image_bp
from .neighborhood_routes import neighborhood_bp
from .chat import chat_bp
from .admin_routes import admin_bp
# لو Blueprint موجود في routes/views.py
from .views_routes import views_bp

from flask import send_from_directory
import os

def register_static_routes(app):
    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        return send_from_directory(os.path.join(os.getcwd(), 'uploads'), filename)

def register_routes(app):
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(favorites_bp, url_prefix="/api/v1/")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(apartment_bp, url_prefix="/api/v1/apartments")
    app.register_blueprint(views_bp)
    app.register_blueprint(review_bp, url_prefix="/api/v1/reviews")
    app.register_blueprint(user_bp, url_prefix="/api/v1/user")
# في app/routes/__init__.py
    app.register_blueprint(neighborhood_bp, url_prefix="/api/v1/")
    app.register_blueprint(chat_bp, url_prefix="/api/v1/chat")
    # ✅ لتفعيل الصور
    register_static_routes(app)
