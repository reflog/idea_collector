import hug
from mongoengine import connect

from ideas import api
from tests import user_token_fixture

user_token = user_token_fixture
con = connect('mongoenginetest', host='mongomock://localhost')


def test_empty_ideas(user_token):
    headers = {"x-access-token": user_token['jwt']}
    response = hug.test.get(api, 'ideas', [], headers=headers)
    assert response.status == hug.HTTP_200
    assert len(response.data) == 0


def test_idea_create_failures(user_token):
    headers = {"x-access-token": user_token['jwt']}
    response = hug.test.post(api, 'ideas', dict(), headers=headers)
    assert response.status == hug.HTTP_400
    response = hug.test.post(api, 'ideas', dict(content=""), headers=headers)
    assert response.status == hug.HTTP_400
    response = hug.test.post(api, 'ideas', dict(content="TEST", confidence=20), headers=headers)
    assert response.status == hug.HTTP_400
    response = hug.test.post(api, 'ideas', dict(content="TEST", ease=-1), headers=headers)
    assert response.status == hug.HTTP_400


def test_idea_create(user_token):
    headers = {"x-access-token": user_token['jwt']}
    response = hug.test.post(api, 'ideas', dict(content="TEST", confidence=3), headers=headers)
    assert response.status == hug.HTTP_200
    assert response.data is not None
    assert response.data['id'] is not None
    assert response.data['content'] == 'TEST'
    assert response.data['average_score'] == 1.0

    response = hug.test.get(api, 'ideas', [], headers=headers)
    assert response.status == hug.HTTP_200
    assert len(response.data) == 1


def test_paging(user_token):
    headers = {"x-access-token": user_token['jwt']}
    for i in range(1, 100):
        hug.test.post(api, 'ideas', dict(content="TEST%d" % i, confidence=i), headers=headers)
    response = hug.test.get(api, 'ideas', [], headers=headers)
    assert response.status == hug.HTTP_200
    assert len(response.data) == 10
    response = hug.test.get(api, 'ideas', dict(page=2), headers=headers)
    assert response.status == hug.HTTP_200
    assert len(response.data) == 10
    assert response.data[0]['content'] == 'TEST11'


def test_idea_scoring(user_token):
    headers = {"x-access-token": user_token['jwt']}
    hug.test.post(api, 'ideas', dict(content="TEST", confidence=3), headers=headers)
    hug.test.post(api, 'ideas', dict(content="TEST2", confidence=10), headers=headers)
    response = hug.test.get(api, 'ideas', [], headers=headers)
    assert response.status == hug.HTTP_200
    assert len(response.data) == 2
    assert response.data[0]['content'] == 'TEST2'
