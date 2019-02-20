import datetime

import hug
import jwt

from ideas.models import User, BlacklistedToken

JWT_SECRET = "SOME-SECRET-HERE"


def token_verify(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithm='HS256')
    except jwt.DecodeError:
        return False


def access_token_create(user: User) -> str:
    return jwt.encode({
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1000),
        'iat': datetime.datetime.utcnow(),
        'identity_claim_key': str(user.id),
        'sub': str(user.id),
        'name': user.name
    }, JWT_SECRET, algorithm='HS256')


def refresh_token_create(user: User) -> str:
    return jwt.encode({
        'identity_claim_key': str(user.id),
        'type': 'refresh'
    }, JWT_SECRET, algorithm='HS256')


@hug.authentication.authenticator
def token_authenticator(request, response, verify_user, context=None, **kwargs):
    """Token verification

    Checks for the Authorization header and verifies using the verify_user function
    """
    token = request.get_header('x-access-token')
    if token:
        if BlacklistedToken.objects(jwt=token).first():
            raise hug.HTTPUnauthorized('Authentication Error', 'Token is blacklisted!')
        try:
            verified_token = verify_user(token)
        except TypeError:
            verified_token = verify_user(token, context)
        except jwt.exceptions.InvalidTokenError:
            raise hug.HTTPUnauthorized('Authentication Error', 'Token is invalid. Expired maybe?')
        if verified_token:
            return verified_token
        else:
            return False
    return None


token_key_authentication = token_authenticator(token_verify)
