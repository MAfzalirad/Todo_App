from ..routers.users import get_db, get_current_user
from fastapi import status
from .utils import *
from ..models import Users

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user_info(test_user):
    response = client.get('/user/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'Abzil'
    assert response.json()['email'] == 'Abzil@gmail.com'
    assert response.json()['first_name'] == 'Abzil'
    assert response.json()['last_name'] == 'Rad'
    assert response.json()['is_active'] == True
    assert response.json()['role'] == 'admin'
    assert response.json()['id'] == 1
    assert response.json()['phone_number'] == '01135511'
    assert bcrypt_context.verify('Abzil123', response.json()['hash_password'])


def test_change_password(test_user):
    response = client.put('/user/password', json={'password':'Abzil123', 'new_password':'admin123'})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert bcrypt_context.verify('admin123', model.hash_password)


def test_change_password_invalid(test_user):
    response = client.put('/user/password', json={'password':'wrong pass', 'new_password':'admin123'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_number(test_user):
    response = client.put('/user/phone_number/11355211')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert model.phone_number == '11355211'
