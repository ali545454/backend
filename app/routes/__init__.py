from flask import send_from_directory
import os

from .auth_routes import auth_bp
from .apartment_routes import apartment_bp
from .reviews_routes import review_bp
from .user_routes import user_bp
from .favorite_routes import favorites_bp
from .image_routes import image_bp
from .neighborhood_routes import neighborhood_bp
from .admin_routes import admin_bp
from .views_routes import views_bp


def register_static_routes(app):

    @app.route("/uploads/<path:filename>")
    def serve_uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


def register_routes(app):

    # Auth
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")

    # Users
    app.register_blueprint(user_bp, url_prefix="/api/v1/user")

    # Apartments
    app.register_blueprint(apartment_bp, url_prefix="/api/v1/apartments")
    app.register_blueprint(image_bp, url_prefix="/api/v1/images")
    app.register_blueprint(review_bp, url_prefix="/api/v1/reviews")
    app.register_blueprint(favorites_bp, url_prefix="/api/v1/favorites")

    # Neighborhoods
    app.register_blueprint(neighborhood_bp, url_prefix="/api/v1/neighborhoods")

    # Admin
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")

    # Views
    app.register_blueprint(views_bp)

    # Static uploads
    register_static_routes(app)