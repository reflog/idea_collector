import hashlib
from datetime import datetime

import hug
from marshmallow import fields
from marshmallow_mongoengine import ModelSchema

from ideas.models import Idea, BlacklistedToken, User


@hug.type(extend=hug.types.text, chain=True)
def non_blacklisted_refresh_token(value):
    if BlacklistedToken.objects(refresh_token=value).first():
        raise ValueError('Supplied token is blacklisted!')
    return value


class MyDateTimeField(fields.DateTime):
    def _deserialize(self, value, attr, data):
        if isinstance(value, datetime):
            return value
        return super()._deserialize(value, attr, data)


class IdeaSchema(ModelSchema):
    class Meta:
        model = Idea
        model_fields_kwargs = {
            'user': {'load_only': True},
            'average_score': {'dump_only': True},
            'id': {'dump_only': True}
        }


class UserSchema(ModelSchema):
    avatar_url = fields.Function(
        lambda obj: "https://www.gravatar.com/avatar/" + hashlib.md5(obj.email.lower().encode()).hexdigest())

    class Meta:
        model = User
        model_fields_kwargs = {
            'password_hash': {'load_only': True},
            'avatar_url': {'dump_only': True},
            'id': {'dump_only': True}
        }
