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
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Try to register with same email
        response = client.post('/api/v1/auth/register', json={
            "fullName": "Another User",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "البريد الإلكتروني مستخدم بالفعل" in data['error']


def test_register_duplicate_phone(client, app):
    with app.app_context():
        # Create a user first
        from app.models.user import User
        user = User(full_name="Test User", email="test2@example.com", phone="123456789")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Try to register with same phone
        response = client.post('/api/v1/auth/register', json={
            "fullName": "Another User",
            "email": "test3@example.com",
            "password": "password123",
            "phone": "123456789"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "رقم الهاتف مستخدم بالفعل" in data['error']