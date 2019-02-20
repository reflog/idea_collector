import binascii
import hashlib
from datetime import datetime

from mongoengine import Document, StringField, EmailField, IntField, ReferenceField, CASCADE, LongField, FloatField

HASH_SALT = b'random stuff here'


def get_password_hash(password):
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), HASH_SALT, 100000)
    return binascii.hexlify(dk).decode()


class User(Document):
    email = EmailField(unique=True)
    name = StringField(required=True)
    password_hash = StringField(required=True)

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = get_password_hash(password)

    def check_password(self, password):
        return self.password_hash == get_password_hash(password)


class BlacklistedToken(Document):
    jwt = StringField()
    refresh_token = StringField()


class Idea(Document):
    content = StringField(max_length=255, required=True, min_length=1)
    impact = IntField(default=0)
    ease = IntField(default=0, min_value=0, max_value=10)
    confidence = IntField(default=0, min_value=0, max_value=10)
    average_score = FloatField(default=0)
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    created_at = LongField(default=lambda: int(datetime.now().timestamp()))

    def clean(self):
        self.average_score = (self.ease + self.impact + self.confidence) / 3
