from flask import Flask
from flask_rest_jsonapi import Api

from . import database
from .resource import UserList, UserDetail, PromptList, PromptDetail, UserRelationship, PromptRelationship

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ultratopsecretkey'
app.config['DEBUG'] = True

database.init_app(app)

db = database.db

api = Api(app)

api.route(UserList, 'user_list', '/users')
api.route(UserDetail, 'user_detail', '/users/<int:id>', '/prompts/<int:prompt_id>/owner')
api.route(UserRelationship, 'user_prompts', '/users/<int:id>/relationships/prompts')
api.route(PromptList, 'prompt_list', '/prompts', '/users/<int:id>/prompts')
api.route(PromptDetail, 'prompt_detail', '/prompts/<int:id>')
api.route(PromptRelationship, 'prompt_user', '/prompts/<int:id>/relationships/owner')

if __name__ == '__main__':
    app.run()
