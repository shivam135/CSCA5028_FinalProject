import pytest
from app import create_app, db
import os

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })

    with app.app_context():
        db.create_all()

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Upload an Image' in rv.data

def test_upload(client):
    data = {
        'image': (open('tests/test_image.jpg', 'rb'), 'test_image.jpg')
    }
    rv = client.post('/upload', data=data, content_type='multipart/form-data')
    assert rv.status_code == 302
    assert rv.headers['Location'].startswith('/result/')

def test_fetch_api_data(client):
    rv = client.get('/fetch')
    assert rv.status_code == 200
