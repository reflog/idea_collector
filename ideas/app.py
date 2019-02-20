import os

import hug
from mongoengine import connect

from ideas import api

connect(host=os.environ.get("MONGODB_URI", 'mongomock://localhost'))


@hug.extend_api()
def apis():
    return [api]


if __name__ == '__main__':
    a = hug.API(__name__).http.serve()
