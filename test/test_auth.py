from ..routers.auth import get_db, authenticate_user, create_access_token, ALGORITHM, SECRET_KEY, get_current_user
from datetime import timedelta
from fastapi import status
from .utils import *
from jose import jwt
import pytest
from fastapi import HTTPException


app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user.username, 'Abzil123', db)
    assert authenticated_user is not None

    non_existing_user = authenticate_user('WrongUsername', 'Abzil123', db)
    assert non_existing_user is False

    wrong_password_user = authenticate_user(test_user.username, 'Wrong Password', db)
    assert wrong_password_user is False

def test_create_access_token():
    db = TestingSessionLocal()
    username = 'testuser'
    id = 1
    role = 'user'
    access_token = create_access_token(username, id, role, expires_delta=timedelta(minutes=30))

    decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['role'] == role
    assert decoded_token['id'] == id


@pytest.mark.asyncio
async def test_get_current_user_valid_token():

    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():

    encode = {'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exinfo:
        await get_current_user(token=token)

    assert exinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

# def test_create_user():
#     request_user = {
#         'username' : 'Abzil',
#         'email' : 'Abzil@gmail.com',
#         'first_name' : 'Abzil',
#         'last_name' : 'Rad',
#         'hash_password' : bcrypt_context.hash('Abzil123'),
#         'is_active' : True,
#         'role' : 'admin',
#         'phone_number' : '01135511'
#     }
#     response = client.post('/auth/', json=request_user)
#     assert response.status_code == status.HTTP_201_CREATED