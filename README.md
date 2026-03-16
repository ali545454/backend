# Backend API (Flask)

## 🔎 Overview
This repository is a Flask-based backend API for an apartment listing and management platform. It includes user authentication, apartment listing CRUD, reviews, favorites, image uploads (Cloudinary), admin management, and view tracking.

The API is organized using Flask blueprints under `/api/v1` and includes cookie-based JWT authentication.

---

## ✅ Quick Start
1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
5. Update `.env` values (DB, Cloudinary, JWT secret, etc.).
6. Run database migrations:
   ```bash
   flask db upgrade
   ```
7. Start the server:
   ```bash
   python run.py
   ```

---

## 🧩 Environment Variables
Copy `.env.example` to `.env` and set the values:

- `JWT_SECRET_KEY` – secret key for JWTs
- `DATABASE_URL` – SQLAlchemy database URL (e.g. `mysql+pymysql://user:pass@host/db`)
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` – for image uploads
- `FLASK_ENV` – `development` or `production`
- `JWT_COOKIE_CSRF_PROTECT` – `true` / `false`
- `JWT_ALGORITHM` – e.g. `HS256`

---

## 🧪 Running Tests
```bash
pytest
```

---

## 📦 Requirements (Key Packages)
- Flask 3
- Flask-SQLAlchemy, SQLAlchemy, Flask-Migrate
- Flask-JWT-Extended (cookie JWT auth)
- Cloudinary + Pillow (image upload/processing)
- Flask-Limiter (rate limiting)
- Marshmallow (validation/serialization)

See `requirements.txt` for full dependency list.

---

## 🚀 API Endpoints (Routes)

### 🔐 Authentication (`/api/v1/auth`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | No | Register a new user (returns cookie JWT).
| POST | `/api/v1/auth/login` | No | Login (returns cookie JWT).
| GET | `/api/v1/auth/profile` | Cookie JWT | Get current user profile.
| POST | `/api/v1/auth/update-password` | Cookie JWT | Update password.
| POST | `/api/v1/auth/logout` | Cookie JWT (optional) | Logout (clears cookie).
| PATCH | `/api/v1/auth/profile/update` | Cookie JWT | Update profile fields.
| GET | `/api/v1/auth/check` | Cookie JWT | Verify auth status.

### 👤 User Endpoints (`/api/v1/user`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/user/<user_id>` | Cookie JWT | Get user basic info (only self).
| PUT | `/api/v1/user/<user_id>` | Cookie JWT | Update user info (email/phone/fullName).

### 🏠 Apartments (`/api/v1/apartments`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/apartments/create` | Cookie JWT | Create a new apartment (multipart form + images).
| GET | `/api/v1/apartments` or `/api/v1/apartments/all_apartments` | No | Get all apartments (supports optional pagination `?paginate=true&page=1&per_page=20`).
| GET | `/api/v1/apartments/verified` | No | Get all verified apartments.
| GET | `/api/v1/apartments/featured` | No | Get the latest 3 apartments (featured).
| GET | `/api/v1/apartments/filter` | No | Filter by query params: `neighborhood_id`, `min_price`, `max_price`, `rooms`.
| GET | `/api/v1/apartments/search` | No | Search by title using `?query=`.
| GET | `/api/v1/apartments/my-apartments` | Cookie JWT | Get current owner’s apartments + stats.
| GET | `/api/v1/apartments/owner-apartments` | Cookie JWT | Get current owner’s apartments (alternate format).
| GET | `/api/v1/apartments/<id>` | No | Get apartment by numeric id.
| PATCH | `/api/v1/apartments/<id>/update` | Cookie JWT | Update apartment (owner only).
| DELETE | `/api/v1/apartments/<uuid>/delete` | Cookie JWT | Delete apartment (owner only).

### ⭐ Favorites (`/api/v1/favorites`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/favorites/add` | Cookie JWT | Add an apartment to favorites (body: `{ apartment_id: "<uuid>" }`).
| DELETE | `/api/v1/favorites/remove/<apartment_uuid>` | Cookie JWT | Remove from favorites.
| GET | `/api/v1/favorites` (also `/list`, `/my`) | Cookie JWT | List favorite apartments.

### 🖼️ Images (`/api/v1/images`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/images/upload-image/<apartment_id>` | Cookie JWT | Upload one or more images to Cloudinary.
| GET | `/api/v1/images/apartment/<apartment_id>/images` | No | List images for an apartment.

### ⭐ Reviews (`/api/v1/reviews`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/reviews/create` (also `/create`) | Cookie JWT | Create a review (body: `apartment_id`, `rating`, `comment`).
| GET | `/api/v1/reviews/apartment/<apartment_id>` | No | List reviews for an apartment.
| DELETE | `/api/v1/reviews/<review_id>/delete` | Cookie JWT | Delete a review (owner only).
| PATCH | `/api/v1/reviews/<review_id>/update` | Cookie JWT | Update a review (owner only).
| GET | `/api/v1/reviews/user` | Cookie JWT | Get reviews by current user.

### 🏘️ Neighborhoods (`/api/v1/neighborhoods`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/neighborhoods` | No | List neighborhoods.
| POST | `/api/v1/neighborhoods/create` | Cookie JWT (admin) | Create a neighborhood (admin only).
| DELETE | `/api/v1/neighborhoods/<id>/delete` | Cookie JWT (admin) | Delete a neighborhood (admin only).

### 🛡️ Admin (`/api/v1/admin`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/admin/register` | No | Create admin account.
| POST | `/api/v1/admin/login` | No | Admin login.
| GET | `/api/v1/admin/stats` | Cookie JWT (admin) | Get admin stats.
| GET | `/api/v1/admin/users` | Cookie JWT (admin) | List users.
| DELETE | `/api/v1/admin/users/<user_uuid>` | Cookie JWT (admin) | Delete a user.
| GET | `/api/v1/admin/apartments` | Cookie JWT (admin) | List apartments.
| DELETE | `/api/v1/admin/apartments/<apartment_uuid>` | Cookie JWT (admin) | Delete an apartment.
| GET | `/api/v1/admin/reviews` | Cookie JWT (admin) | List reviews.
| DELETE | `/api/v1/admin/reviews/<review_id>` | Cookie JWT (admin) | Delete a review.
| GET | `/api/v1/admin/neighborhoods` | Cookie JWT (admin) | List neighborhoods.
| POST | `/api/v1/admin/neighborhoods` | Cookie JWT (admin) | Create neighborhood.
| DELETE | `/api/v1/admin/neighborhoods/<neighborhood_id>` | Cookie JWT (admin) | Delete neighborhood.

### 👀 Views Tracking (`/api/views`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/views/track/<uuid>` | No | Track a view for an apartment (optionally includes user if authenticated).
| GET | `/api/views/owner/details` | Cookie JWT | Get view stats for current owner’s listings.

---

## 🗂️ Static Uploads
Uploaded files are served from the `UPLOAD_FOLDER` config path via:
- `GET /uploads/<filename>`

---

## 🛠️ Notes / Tips
- Authentication relies on cookie-based JWT. Make sure the client sends/receives cookies.
- Uploads use Cloudinary; set credentials in `.env`.
- To inspect models and database schema, see `app/models/`.

---

*Generated automatically from the repository structure.*
