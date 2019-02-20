import hug

from ideas import api
from tests import user_token_fixture

user_token = user_token_fixture


def test_duplicate_email(user_token):
    response = hug.test.post(api, '/users', dict(email="test@test.com", password="test", name="ME"))
    assert response.status == hug.HTTP_400


def test_login(user_token):
    response = hug.test.post(api, '/access-tokens', dict(email="test@test.com", password="test"))
    assert response.status == hug.HTTP_200
    assert response.data is not None
    assert response.data['jwt'] is not None


def test_second_user(user_token):
    response = hug.test.post(api, '/users', dict(email="test2@test.com", password="test", name="ME"))
    assert response.status == hug.HTTP_200


def test_get_user(user_token):
    headers = {"x-access-token": user_token['jwt']}
    response = hug.test.get(api, '/me', [], headers=headers)
    assert response.status == hug.HTTP_200
    assert response.data is not None
    assert response.data['email'] == "test@test.com"


def test_refresh(user_token):
    headers = {"x-access-token": user_token['jwt']}
    response = hug.test.post(api, '/access-tokens/refresh', dict(refresh_token=user_token['refresh_token']),
                             headers=headers)
    assert response.status == hug.HTTP_200
    assert response.data is not None
    assert response.data['jwt'] is not None


def test_logout(user_token):
    headers = {"x-access-token": user_token['jwt']}
    response = hug.test.delete(api, '/access-tokens', dict(refresh_token=user_token['refresh_token']), headers=headers)
    assert response.status == hug.HTTP_200
    response = hug.test.post(api, '/access-tokens/refresh', dict(refresh_token=user_token['refresh_token']),
                             headers=headers)
    assert response.status == hug.HTTP_400
