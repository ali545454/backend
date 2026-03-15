from app import create_app, db
from app.models.user import User

app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'SQLALCHEMY_ENGINE_OPTIONS': {}})
with app.app_context():
    db.create_all()
    u = User(full_name='Test', email='test@example.com')
    u.set_password('StrongPass1!')
    db.session.add(u)
    db.session.commit()
    client = app.test_client()
    r = client.post('/api/v1/auth/login', json={'email': 'test@example.com', 'password': 'StrongPass1!'})
    print('status', r.status_code)
    print('data', r.get_json())
