import pytest
from database import app

def test_home():
    client=app.test_client()
    response=client.get("/")
    assert b"New Arrivals" in response.data

# def test_login():
#     client=app.test_client()
#     response=client.get("/login")
#     assert b"New Arrivals" in response.data

def test_register():
    client=app.test_client()
    response=client.get("/login")
    assert b"Sign In" in response.data