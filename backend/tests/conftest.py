
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.driver import Driver
from app.core.auth import create_access_token

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def db_session():
    # Ensure tables exist
    from app.core.database import Base
    # Must import ALL models to register them with Base.metadata
    from app.models.user import User
    from app.models.driver import Driver
    from app.models.gamification import Badge, UserBadge
    from app.models.chat import ChatRoom, ChatMessage
    from app.models.ride import Ride
    from app.models.incident import Incident
    
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="module")
def test_user(db_session):
    user = db_session.query(User).filter(User.email == "test_user@example.com").first()
    if not user:
        user = User(
            id="test_user_id",
            phone_number="123456789",
            email="test_user@example.com",
            full_name="Test User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

@pytest.fixture(scope="module")
def mock_user_token(test_user):
    return create_access_token(data={"sub": test_user.id, "role": "passenger"})

@pytest.fixture(scope="module")
def test_driver(db_session):
    user = db_session.query(User).filter(User.email == "test_driver@example.com").first()
    if not user:
        user = User(
            id="test_driver_id",
            phone_number="987654321",
            email="test_driver@example.com",
            full_name="Test Driver",
            is_active=True,
            is_driver=True
        )
        db_session.add(user)
        # Add Driver profile too
        driver = Driver(
            id="test_driver_id",
            user_id="test_driver_id",
            license_number="TEST_LIC",
            vehicle_type="moto",
            status="offline"
        )
        db_session.add(driver)
        db_session.commit()
        db_session.refresh(user)
    return user

@pytest.fixture(scope="module")
def mock_driver_token(test_driver):
    return create_access_token(data={"sub": test_driver.id, "role": "driver"})
