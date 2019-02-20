import hug
import pytest
from mongoengine import connect

from ideas import api
from ideas.authentication import token_verify
from ideas.models import User


@pytest.fixture
def user_token_fixture():
    con = connect('mongoenginetest', host='mongomock://localhost')
    response = hug.test.post(api, '/users', dict(email="test@test.com", password="test", name="ME"))
    assert response.status == hug.HTTP_200
    assert response.data is not None
    assert response.data['jwt'] is not None
    assert response.data['refresh_token'] is not None
    token = token_verify(response.data['jwt'])
    assert token is not None
    yield response.data
    User.objects(id=token['sub']).delete()
    con.close()
