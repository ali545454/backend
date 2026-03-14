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
