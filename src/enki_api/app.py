from datetime import datetime

from flask import Flask, request
from flask_rest_jsonapi import Api
from flask_cors import CORS

from . import database
from .model import Chat
from gpt_utils.core import GPT
from gpt_utils.prompt import ChatPrompt

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

api.route(ChatList, 'chat_list', '/chats', '/users/<int:id>/chats')
api.route(ChatDetail, 'chat_detail', '/chats/<int:id>')
api.route(ChatRelationship, 'chat_user', '/chats/<int:id>/relationships/owner')
api.route(ChatRelationship, 'chat_prompt', '/chats/<int:id>/relationships/prompt')


@app.route('/chats/<int:chat_id>/messages', methods=['POST'])
def post_message(chat_id):
    # print(request.json)
    # print(request.args)
    message = request.values.get('message')
    # print(message)
    # return message
    chat = Chat.query.filter_by(id=chat_id)[0]
    prompt = ChatPrompt(
        chat.prompt.bot_name,
        chat.prompt.human_name,
        *chat.prompt.messages,
        intro_text=chat.prompt.intro_text
    )
    prompt.messages += chat.messages
    reply = GPT(
        engine="davinci",
        stop='\n',
        max_tokens=chat.prompt.max_tokens,
        temperature=chat.prompt.temperature,
        presence_penalty=chat.prompt.presence_penalty,
        frequency_penalty=chat.prompt.frequency_penalty,
    ).response(prompt.format(message))

    chat.messages += [[message, reply]]
    chat.date_updated = datetime.now()
    db.session.add(chat)
    db.session.commit()
    return reply


if __name__ == '__main__':
    app.run()
