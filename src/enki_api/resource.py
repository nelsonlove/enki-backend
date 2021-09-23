from flask_rest_jsonapi import ResourceList, ResourceDetail, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.exc import NoResultFound

from enki_api.database import db
from enki_api.model import User, Prompt, Chat, Message
from enki_api.schema import UserSchema, PromptSchema, ChatSchema, MessageSchema


def query_from_related(data_model, session, view_kwargs, related):
    query_ = session.query(data_model)
    for model in related:
        parameter = model.__name__.lower() + '_id'
        value = view_kwargs.get(parameter)
        if value:
            try:
                session.query(model).filter_by(id=value).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': parameter},
                                     f'{model.__name__}: {value} not found')
            else:
                query_ = query_.join(model).filter(model.id == value)

    return query_


def get_related(session, view_kwargs, related, relation):
    for model in related:
        parameter = model.__name__.lower() + '_id'
        value = view_kwargs.get(parameter)
        if value:
            try:
                obj = session.query(model).filter_by(id=value).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': parameter},
                                     f'{model.__name__}: {value} not found')
            else:
                if relation(obj) is not None:
                    view_kwargs['id'] = relation(obj).id
                else:
                    view_kwargs['id'] = None


class UserList(ResourceList):
    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User,
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls, 'user_list', '/users')


class UserDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        get_related(self.session, view_kwargs, [Prompt, Chat], lambda obj: obj.owner)

    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User,
        'methods': {
            'before_get_object': before_get_object,
        }
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls,
                  'user_detail',
                  '/users/<int:id>',
                  '/prompts/<int:prompt_id>/owner',
                  '/chats/<int:chat_id>/owner'
                  )


class UserRelationship(ResourceRelationship):
    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls, 'user_prompts', '/users/<int:id>/relationships/prompts')
        api.route(cls, 'user_chats', '/users/<int:id>/relationships/chats')


# might want to get public resources only for list endpoints


class PromptList(ResourceList):
    def query(self, view_kwargs):
        return query_from_related(Prompt, self.session, view_kwargs, [User])

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('user_id') is not None:
            user = self.session.query(User).filter_by(id=view_kwargs['user_id']).one()
            data['owner_id'] = user.id

    schema = PromptSchema
    data_layer = {
        'session': db.session,
        'model': Prompt,
        'methods': {
            'query': query,
            'before_create_object': before_create_object,
        }
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls,
                  'prompt_list',
                  '/prompts',
                  '/users/<int:user_id>/prompts'
                  )


class PromptDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        get_related(self.session, view_kwargs, [Message, Chat], lambda obj: obj.prompt)

    schema = PromptSchema
    data_layer = {
        'session': db.session,
        'model': Prompt,
        'methods': {
            'before_get_object': before_get_object,
        }
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls,
                  'prompt_detail',
                  '/prompts/<int:id>',
                  '/chats/<int:chat_id>/prompt',
                  '/messages/<int:message_id>/prompt'
                  )


class PromptRelationship(ResourceRelationship):
    schema = PromptSchema
    data_layer = {
        'session': db.session,
        'model': Prompt
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls, 'prompt_user', '/prompts/<int:id>/relationships/owner')
        api.route(cls, 'prompt_chats', '/prompts/<int:id>/relationships/chats')
        api.route(cls, 'prompt_messages', '/prompts/<int:id>/relationships/messages')


class ChatList(ResourceList):
    def query(self, view_kwargs):
        return query_from_related(Chat, self.session, view_kwargs, [User, Prompt])

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('prompt_id') is not None:
            prompt = self.session.query(Prompt).filter_by(id=view_kwargs['prompt_id']).one()
            data['prompt_id'] = prompt.id

    schema = ChatSchema
    data_layer = {
        'session': db.session,
        'model': Chat,
        'methods': {
            'query': query,
            'before_create_object': before_create_object,
        }
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls,
                  'chat_list',
                  '/chats',
                  '/users/<int:user_id>/chats',
                  '/prompts/<int:prompt_id>/chats'
                  )


class ChatDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        get_related(self.session, view_kwargs, [Message], lambda obj: obj.chat)

    schema = ChatSchema
    data_layer = {
        'session': db.session,
        'model': Chat,
        'methods': {
            'before_get_object': before_get_object
        }
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls,
                  'chat_detail',
                  '/chats/<int:id>',
                  '/messages/<int:message_id>/chat'
                  )


class ChatRelationship(ResourceRelationship):
    schema = ChatSchema
    data_layer = {
        'session': db.session,
        'model': Chat
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls, 'chat_user', '/chats/<int:id>/relationships/owner')
        api.route(cls, 'chat_prompt', '/chats/<int:id>/relationships/prompt')
        api.route(cls, 'chat_messages', '/chats/<int:id>/relationships/messages')


class MessageList(ResourceList):
    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('chat_id') is not None:
            chat = self.session.query(Chat).filter_by(id=view_kwargs['chat_id']).one()
            data['chat_id'] = chat.id

    def query(self, view_kwargs):
        query_ = self.session.query(Message)
        if view_kwargs.get('prompt_id') is not None:
            value = view_kwargs.get('prompt_id')
            try:
                self.session.query(Prompt).filter_by(id=value).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'prompt_id'},
                                     f'Prompt: {value} not found')
            else:
                query_ = query_.join(Prompt).filter(Prompt.id == value)
        elif view_kwargs.get('chat_id') is not None:
            value = view_kwargs.get('chat_id')
            try:
                chat = self.session.query(Chat).filter_by(id=value).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'chat_id'},
                                     f'Chat: {value} not found')
            else:
                prompt_messages = query_.join(Prompt).filter(Prompt.id == chat.prompt.id)
                chat_messages = query_.join(Chat).filter(Chat.id == value)
                query_ = chat_messages.union(prompt_messages)

        return query_

    def after_post(self, result):
        message_id = result[0]['data']['id']
        message = Message.query.filter_by(id=message_id).one()
        message.check_if_needs_reply()

    schema = MessageSchema
    data_layer = {
        'session': db.session,
        'model': Message,
        'methods': {
            'query': query,
            'before_create_object': before_create_object,
            'after_post': after_post,
        }
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls,
                  'message_list',
                  '/messages',
                  '/prompts/<int:prompt_id>/messages',
                  '/chats/<int:chat_id>/messages'
                  )


class MessageDetail(ResourceDetail):
    schema = MessageSchema
    data_layer = {
        'session': db.session,
        'model': Message
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls, 'message_detail', '/messages/<int:id>')


class MessageRelationship(ResourceRelationship):
    schema = MessageSchema
    data_layer = {
        'session': db.session,
        'model': Message
    }

    @classmethod
    def add_routes(cls, api):
        api.route(cls, 'message_chat', '/messages/<int:id>/relationships/chat')
        api.route(cls, 'message_prompt', '/messages/<int:id>/relationships/prompt')
