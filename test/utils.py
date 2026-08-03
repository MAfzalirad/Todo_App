from sqlalchemy import create_engine, text
from ..database import Base
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..models import Todos, Users
from fastapi.testclient import TestClient
import pytest
from passlib.context import CryptContext



SQLALCHEMY_DATABASE_URL = 'sqlite:///./testtodos.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread": False}, poolclass=StaticPool)


TestingSessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username':'Abzil', 'id':1, 'user_role':'admin'}


client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title = 'Learn to code',
        description = 'fast api',
        priority = 1,
        complete = False,
        owner_id = 1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        user_name = 'Abzil',
        email = 'Abzil@gmail.com',
        first_name = 'Abzil',
        last_name = 'Rad',
        hash_password = bcrypt_context.hash('Abzil123'),
        is_active = True,
        role = 'admin',
        phone_number = '01135511'
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()