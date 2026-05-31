import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app
from backend.database import Base, get_db

# Use a separate in-memory database for tests — never touches wanderwise.db
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Replace the real DB dependency with the test DB
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    # Create all tables before each test, drop after
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(client):
    # Creates a user and returns their data + token
    signup_response = client.post("/signup", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    login_response = client.post("/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    
    token = login_response.json()["access_token"]
    
    return {
        "id": signup_response.json()["id"],
        "email": "test@example.com",
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }