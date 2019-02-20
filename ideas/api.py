import bson
import hug

from ideas import directives
from ideas.authentication import access_token_create, refresh_token_create, token_key_authentication, token_verify
from ideas.models import User, get_password_hash, Idea, BlacklistedToken
from ideas.validation import IdeaSchema, non_blacklisted_refresh_token, UserSchema


@hug.not_found()
def not_found():
    return {'Nothing': 'to see here'}


@hug.post('/users')
def create_user(
        email: hug.types.text,
        password: hug.types.text,
        name: hug.types.text
):
    if User.objects(email=email).first():
        raise hug.HTTPBadRequest('Cannot signup', 'User with email {0} already exists.'.format(email))

    user = User(email=email, name=name)
    user.password = password
    user.save()
    return dict(jwt=access_token_create(user), refresh_token=refresh_token_create(user))


@hug.post('/access-tokens')
def login_user(email: hug.types.text, password: hug.types.text):
    h = get_password_hash(password)
    user = User.objects(email=email, password_hash=h).first()
    if not user:
        raise hug.HTTPUnauthorized("Unauthorized", "Wrong password/email combination")
    return dict(jwt=access_token_create(user), refresh_token=refresh_token_create(user))


@hug.delete('/access-tokens')
def logout_user(refresh_token: non_blacklisted_refresh_token,
                access_token: directives.access_token,
                requires=token_key_authentication):
    token = token_verify(refresh_token)
    user_id = token['identity_claim_key']
    user = User.objects(id=user_id).first()
    if not user:
        raise hug.HTTPUnauthorized("Unauthorized", "Wrong token content")
    BlacklistedToken(jwt=access_token, refresh_token=refresh_token).save()


@hug.post('/access-tokens/refresh')
def refresh_user(refresh_token: non_blacklisted_refresh_token,
                 requires=token_key_authentication):
    token = token_verify(refresh_token)
    user_id = token['identity_claim_key']
    user = User.objects(id=user_id).first()
    if not user:
        raise hug.HTTPUnauthorized("Unauthorized", "Wrong token content")

    return dict(jwt=access_token_create(user))


@hug.get('/ideas', requires=token_key_authentication)
def get_ideas(user: directives.user, page: hug.types.number = 1, page_size: hug.types.number = 10):
    items_per_page = page_size
    offset = (page - 1) * items_per_page

    return [IdeaSchema().dump(i).data for i in
            Idea.objects(user=user).order_by("-average_score").skip(offset).limit(items_per_page)]


@hug.delete('/ideas/{id}', requires=token_key_authentication, status_code=hug.falcon.HTTP_204)
def delete_idea(user: directives.user, id: hug.types.text):
    idea = Idea.objects(user=user, id=bson.ObjectId(id)).first()
    if not idea:
        raise hug.HTTPNotFound()
    idea.delete()


@hug.put('/ideas/{id}', requires=token_key_authentication, status_code=hug.falcon.HTTP_204)
def update_idea(user: directives.user, id: hug.types.text, body: IdeaSchema()) -> IdeaSchema():
    idea = Idea.objects(user=user, id=bson.ObjectId(id)).first()
    if not idea:
        raise hug.HTTPNotFound()
    result = IdeaSchema().update(idea, IdeaSchema().dump(body).data)
    result.data.save()
    return result.data


@hug.post('/ideas', requires=token_key_authentication)
def create_idea(body: IdeaSchema(),
                user: directives.user) -> IdeaSchema():
    body.user = user
    body.save()
    return body


@hug.get('/me', requires=token_key_authentication)
def get_user(user: directives.user) -> UserSchema():
    return user
