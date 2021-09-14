from flask import Flask
from flask_rest_jsonapi import Api

from .resource import UserList, UserDetail
from . import database

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ultratopsecretkey'
app.config['DEBUG'] = True

database.init_app(app)

db = database.db

api = Api(app)
api.route(UserList, 'user_list', '/users')
api.route(UserDetail, 'user_detail', '/users/<int:id>')


if __name__ == '__main__':
    app.run()
