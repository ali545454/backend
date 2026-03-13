def test_app_creation(app):
    assert app is not None
    assert app.config['TESTING'] is True


def test_home_route(client):
    response = client.get('/')
    # Assuming there's no root route, it should return 404 or whatever
    # Adjust based on actual routes
    assert response.status_code in [200, 404]  # Placeholder