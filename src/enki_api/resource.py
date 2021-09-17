from flask import request
from flask_rest_jsonapi import ResourceList, ResourceDetail, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.exc import NoResultFound

from .database import db
from .model import User, Prompt, Chat
from .schema import UserSchema, PromptSchema, ChatSchema


class UserList(ResourceList):
    def query(self, view_kwargs):
        # Looks up user from auth_id
        query_ = self.session.query(User)
        auth_id = request.values.get('auth_id')
        if auth_id is not None:
            try:
                query_ = self.session.query(User).filter_by(auth_id=auth_id)
                user = query_.one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'id'}, "User: {} not found".format(auth_id))
            else:
                # user.date_modified = db.func.now()
                user.touch()

        return query_

    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User,
        'methods': {
            'query': query,
        }
    }


class UserDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        # /prompts/<int:prompt_id>/owner
        if view_kwargs.get('prompt_id') is not None:
            try:
                # Get the prompt with matching ID
                prompt = self.session.query(Prompt).filter_by(id=view_kwargs['prompt_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'prompt_id'},
                                     "Prompt: {} not found".format(view_kwargs['prompt_id']))
            else:
                if prompt.owner is not None:
                    view_kwargs['id'] = prompt.owner.id
                else:
                    view_kwargs['id'] = None

        # /chats/<int:chat_id>/owner
        elif view_kwargs.get('chat_id') is not None:
            try:
                # Get the chat with matching ID
                chat = self.session.query(Chat).filter_by(id=view_kwargs['chat_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'chat_id'},
                                     "Chat: {} not found".format(view_kwargs['chat_id']))
            else:
                if chat.owner is not None:
                    view_kwargs['id'] = chat.owner.id
                else:
                    view_kwargs['id'] = None

    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User,
        'methods': {
            'before_get_object': before_get_object,
        }
    }


class UserRelationship(ResourceRelationship):
    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User
    }


# might want to get public resources only for list endpoints


class PromptList(ResourceList):
    def query(self, view_kwargs):
        query_ = self.session.query(Prompt)
        # /users/<int:id>/prompts
        # Get user same as above
        if view_kwargs.get('id') is not None:
            try:
                self.session.query(User).filter_by(id=view_kwargs['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'id'}, "User: {} not found".format(view_kwargs['id']))
            else:
                query_ = query_.join(User).filter(User.id == view_kwargs['id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        # for POST method?
        if view_kwargs.get('id') is not None:
            user = self.session.query(User).filter_by(id=view_kwargs['id']).one()
            data['user_id'] = user.id

    schema = PromptSchema
    data_layer = {
        'session': db.session,
        'model': Prompt,
        'methods': {
            'query': query,
            'before_create_object': before_create_object,
        }
    }


class PromptDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        # /chats/<int:chat_id>/prompt
        if view_kwargs.get('chat_id') is not None:
            try:
                chat = self.session.query(Chat).filter_by(id=view_kwargs['chat_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'chat_id'},
                                     "Chat: {} not found".format(view_kwargs['chat_id']))
            else:
                if chat.prompt is not None:
                    view_kwargs['id'] = chat.prompt.id
                else:
                    view_kwargs['id'] = None

    schema = PromptSchema
    data_layer = {
        'session': db.session,
        'model': Prompt,
        'methods': {
            'before_get_object': before_get_object,
        }
    }


class PromptRelationship(ResourceRelationship):
    schema = PromptSchema
    data_layer = {
        'session': db.session,
        'model': Prompt
    }


class ChatList(ResourceList):
    def query(self, view_kwargs):
        query_ = self.session.query(Chat)
        if view_kwargs.get('id') is not None:
            try:
                self.session.query(User).filter_by(id=view_kwargs['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'id'}, "User: {} not found".format(view_kwargs['id']))
            else:
                query_ = query_.join(User).filter(User.id == view_kwargs['id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('id') is not None:
            user = self.session.query(User).filter_by(id=view_kwargs['id']).one()
            data['user_id'] = user.id

    schema = ChatSchema
    data_layer = {
        'session': db.session,
        'model': Chat,
        'methods': {
            'query': query,
            'before_create_object': before_create_object,
        }
    }


class ChatDetail(ResourceDetail):
    schema = ChatSchema
    data_layer = {
        'session': db.session,
        'model': Chat
    }


class ChatRelationship(ResourceRelationship):
    schema = ChatSchema
    data_layer = {
        'session': db.session,
        'model': Chat
    }
