import pytest


@pytest.fixture
def client():
    from app import app as main_app
    main_app.testing = True
    main_app.config['MONGO_HOST'] = 'mongomock://localhost'
    return main_app.test_client()

def test_null(client):
    '''Tests aren't currently implemented. Mock a thing so pytest can succeed'''
    pass
