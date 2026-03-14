from app import db

def test_app_creation(app):
    assert app is not None
    assert app.config['TESTING'] is True


def test_home_route(client):
    response = client.get('/')
    # Assuming there's no root route, it should return 404 or whatever
    # Adjust based on actual routes
    assert response.status_code in [200, 404]  # Placeholder


def test_register_duplicate_email(client, app):
    with app.app_context():
        # Create a user first
        from app.models.user import User
        user = User(full_name="Test User", email="test@example.com", phone="123456789")
        user.set_password("StrongPass1!")
        db.session.add(user)
        db.session.commit()

        # Try to register with same email
        response = client.post('/api/v1/auth/register', json={
            "fullName": "Another User",
            "email": "test@example.com",
            "password": "StrongPass1!"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "البريد الإلكتروني مستخدم بالفعل" in data['error']


def test_register_duplicate_phone(client, app):
    with app.app_context():
        # Create a user first
        from app.models.user import User
        user = User(full_name="Test User", email="test2@example.com", phone="123456789")
        user.set_password("StrongPass1!")
        db.session.add(user)
        db.session.commit()

        # Try to register with same phone
        response = client.post('/api/v1/auth/register', json={
            "fullName": "Another User",
            "email": "test3@example.com",
            "password": "StrongPass1!",
            "phone": "123456789"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "رقم الهاتف مستخدم بالفعل" in data['error']

def test_clean_apartment_and_review_routes_exist(app):
    rules = {rule.rule for rule in app.url_map.iter_rules()}

    # Clean apartment routes (without duplicated segment names)
    assert '/api/v1/apartments/' in rules
    assert '/api/v1/apartments/search' in rules
    assert '/api/v1/apartments/filter' in rules
    assert '/api/v1/apartments/verified' in rules

    # Clean review routes under /api/v1/reviews
    assert '/api/v1/reviews/create' in rules
    assert '/api/v1/reviews/user' in rules
    assert '/api/v1/reviews/apartment/<int:apartment_id>' in rules


def test_old_duplicated_routes_still_exist_for_backward_compat(app):
    rules = {rule.rule for rule in app.url_map.iter_rules()}

    assert '/api/v1/apartments/apartments/search' in rules
    assert '/api/v1/apartments/apartments/filter' in rules
    assert '/api/v1/reviews/reviews/create' in rules


def test_apartment_listing_pagination_contract(client):
    response = client.get('/api/v1/apartments/?paginate=true&page=1&per_page=5')
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert 'items' in data
    assert 'pagination' in data
    assert data['pagination']['page'] == 1
    assert data['pagination']['per_page'] == 5


def test_apartment_listing_default_contract_is_list(client):
    response = client.get('/api/v1/apartments/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_google_login_creates_new_user(client, monkeypatch):
    from app.routes import auth_routes

    def fake_verify(_token):
        return {
            "email": "google_user@example.com",
            "sub": "google-sub-123",
            "name": "Google Tester",
            "email_verified": True,
        }

    monkeypatch.setattr(auth_routes, "verify_google_id_token", fake_verify)

    response = client.post('/api/v1/auth/google-login', json={"id_token": "dummy"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["user"]["email"] == "google_user@example.com"
    assert data["user"]["google_id"] == "google-sub-123"


def test_google_login_links_existing_email(client, app, monkeypatch):
    from app.models.user import User
    from app.routes import auth_routes

    with app.app_context():
        user = User(full_name="Existing User", email="existing@example.com", phone="111222333")
        user.set_password("StrongPass1!")
        db.session.add(user)
        db.session.commit()

    def fake_verify(_token):
        return {
            "email": "existing@example.com",
            "sub": "google-linked-sub",
            "name": "Existing User",
            "email_verified": True,
        }

    monkeypatch.setattr(auth_routes, "verify_google_id_token", fake_verify)

    response = client.post('/api/v1/auth/google-login', json={"credential": "dummy"})
    assert response.status_code == 200

    with app.app_context():
        linked = User.query.filter_by(email="existing@example.com").first()
        assert linked.google_id == "google-linked-sub"


def test_google_login_invalid_token(client, monkeypatch):
    from app.routes import auth_routes

    def fake_verify(_token):
        raise ValueError("invalid")

    monkeypatch.setattr(auth_routes, "verify_google_id_token", fake_verify)

    response = client.post('/api/v1/auth/google-login', json={"id_token": "bad"})
    assert response.status_code == 401
    data = response.get_json()
    assert "Invalid Google token" in data["error"]
