from flask_rest_jsonapi import ResourceList, ResourceDetail, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.exc import NoResultFound

from src.enki_api.database import db
from src.enki_api.model import User, Prompt  # , Chat
from src.enki_api.schema import UserSchema, PromptSchema


class UserList(ResourceList):
    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User,
    }


class UserDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('prompt_id') is not None:
            try:
                prompt = self.session.query(Prompt).filter_by(id=view_kwargs['prompt_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'prompt_id'},
                                     "Prompt: {} not found".format(view_kwargs['prompt_id']))
            else:
                if prompt.owner is not None:
                    view_kwargs['id'] = prompt.owner.id
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
    data_layer = {'session': db.session,
                  'model': User}


class PromptList(ResourceList):
    def query(self, view_kwargs):
        query_ = self.session.query(Prompt)
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
    schema = PromptSchema
    data_layer = {'session': db.session,
                  'model': Prompt}


class PromptRelationship(ResourceRelationship):
    schema = PromptSchema
    data_layer = {'session': db.session,
                  'model': Prompt}
