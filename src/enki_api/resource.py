from flask_rest_jsonapi import ResourceList, ResourceDetail

from src.enki_api.database import db
from src.enki_api.model import User
from src.enki_api.schema import UserSchema


class UserList(ResourceList):
    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User,
    }


class UserDetail(ResourceDetail):
    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User,
    }
