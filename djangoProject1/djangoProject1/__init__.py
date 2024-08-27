import mongoengine

from djangoProject1.settings import MONGO_CONNECTION_STRING

mongoengine.connect(host=MONGO_CONNECTION_STRING)
