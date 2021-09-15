from flask import Flask
from flask_rest_jsonapi import Api
from flask_cors import CORS

from . import database
from .resource import (
    UserList,
    UserDetail,
    UserRelationship,
    PromptList,
    PromptDetail,
    PromptRelationship,
    ChatList,
    ChatDetail,
    ChatRelationship
)

app = Flask(__name__)

CORS(app)

app.config['SECRET_KEY'] = 'ultratopsecretkey'
app.config['DEBUG'] = True

database.init_app(app)

db = database.db

api = Api(app)
api.route(UserList, 'user_list', '/users')

api.route(UserDetail, 'user_detail',
          '/users/<int:id>',
          '/prompts/<int:prompt_id>/owner',
          '/chats/<int:chat_id>/owner'
          )
api.route(UserRelationship, 'user_prompts', '/users/<int:id>/relationships/prompts')
api.route(UserRelationship, 'user_chats', '/users/<int:id>/relationships/chats')

api.route(PromptList, 'prompt_list', '/prompts', '/users/<int:id>/prompts')
api.route(PromptDetail, 'prompt_detail',
          '/prompts/<int:id>',
          '/chats/<int:chat_id>/prompt'
          )
api.route(PromptRelationship, 'prompt_user', '/prompts/<int:id>/relationships/owner')
api.route(PromptRelationship, 'prompt_chats', '/prompts/<int:id>/relationships/chats')

api.route(ChatList, 'chat_list', '/chats')
api.route(ChatDetail, 'chat_detail', '/chats/<int:id>')
api.route(ChatRelationship, 'chat_user', '/chats/<int:id>/relationships/owner')
api.route(ChatRelationship, 'chat_prompt', '/chats/<int:id>/relationships/prompt')

if __name__ == '__main__':
    app.run()
