from typing import Optional

import bson
import hug
from hug import HTTPUnauthorized

from ideas.models import User


@hug.directive()
def access_token(default=None, request=None, **kwargs) -> Optional[str]:
    """Returns the current access token from the headers"""
    return request.get_header('x-access-token')


@hug.directive()
def user(default=None, request=None, **kwargs) -> User:
    """Returns the current logged in user"""
    user_data = request and request.context.get('user', None) or default
    u = User.objects.get(id=bson.objectid.ObjectId(user_data['sub']))
    if not u:
        raise HTTPUnauthorized('Authentication Error', 'Token doesn\' match any user')
    return u
