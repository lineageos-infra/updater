import os
import json

import pytest
import requests


@pytest.fixture
def blobs(scope="session"):
    print("downloading blobs...")
    with open("devices.json", "w") as f:
        data = requests.get("https://raw.githubusercontent.com/LineageOS/hudson/master/updater/devices.json")
        f.write(data.text)

    with open("device_deps.json", "w") as f:
        data = requests.get("https://raw.githubusercontent.com/LineageOS/hudson/master/updater/device_deps.json")
        f.write(data.text)
    yield
    print("removing blobs...")
    os.remove("devices.json")
    os.remove("device_deps.json")

@pytest.fixture
def client(blobs):
    from app import app as main_app
    main_app.testing = True
    main_app.config['MONGO_HOST'] = 'mongomock://localhost'
    return main_app.test_client()

def test_null(client):
    '''Tests aren't currently implemented. Mock a thing so pytest can succeed'''
    pass
