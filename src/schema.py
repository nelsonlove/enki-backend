import re

from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship


def underscore_to_camel(name):
    under_pat = re.compile(r'_([a-z])')
    return under_pat.sub(lambda x: x.group(1).upper(), name)


class UserSchema(Schema):
    class Meta:
        type_ = 'user'
        self_view = 'user_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'user_list'
        inflect = underscore_to_camel

    # TODO move assets_last_active here?
    id = fields.Integer(as_string=True)
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime()

    auth_id = fields.Str()  # from auth0
    nickname = fields.Str()
    api_key = fields.Str(load_only=True)
    has_api_key = fields.Function(lambda obj: bool(obj.api_key), dump_only=True)
    invite_code = fields.Str(load_only=True)
    has_invite_code = fields.Function(lambda obj: bool(obj.invite_code), dump_only=True)

    visible = fields.Bool()
    visible_chats = fields.Bool()
    visible_prompts = fields.Bool()

    prompts = Relationship(self_view='user_prompts',
                           self_view_kwargs={'id': '<id>'},
                           related_view='prompt_list',
                           related_view_kwargs={'user_id': '<id>'},
                           many=True,
                           schema='PromptSchema',
                           type_='prompt')

    chats = Relationship(self_view='user_chats',
                         self_view_kwargs={'id': '<id>'},
                         related_view='chat_list',
                         related_view_kwargs={'user_id': '<id>'},
                         many=True,
                         schema='ChatSchema',
                         type_='chat')


class PromptSchema(Schema):
    class Meta:
        type_ = 'prompt'
        self_view = 'prompt_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'prompt_list'
        inflect = underscore_to_camel

    id = fields.Integer(as_string=True, dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime()

    visible = fields.Bool()

    # TODO validation should probably go in here

    intro = fields.Str()
    bot = fields.Str()
    human = fields.Str()

    temperature = fields.Float()
    variety = fields.Float()
    verbosity = fields.Int()

    owner = Relationship(self_view='prompt_user',
                         self_view_kwargs={'id': '<id>'},
                         related_view='user_detail',
                         related_view_kwargs={'prompt_id': '<id>'},
                         schema='UserSchema',
                         type_='user')

    chats = Relationship(self_view='prompt_chats',
                         self_view_kwargs={'id': '<id>'},
                         related_view='chat_list',
                         related_view_kwargs={'prompt_id': '<id>'},
                         many=True,
                         schema='ChatSchema',
                         type_='chat')

    messages = Relationship(self_view='prompt_messages',
                            self_view_kwargs={'id': '<id>'},
                            related_view='message_list',
                            related_view_kwargs={'prompt_id': '<id>'},
                            many=True,
                            schema='MessageSchema',
                            type_='message')


class ChatSchema(Schema):
    class Meta:
        type_ = 'chat'
        self_view = 'chat_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'chat_list'
        inflect = underscore_to_camel

    id = fields.Integer(as_string=True, dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime()

    visible = fields.Bool()
    active = fields.Bool()

    owner_id = fields.Integer(as_string=True, load_only=True)
    owner = Relationship(self_view='chat_user',
                         self_view_kwargs={'id': '<id>'},
                         related_view='user_detail',
                         related_view_kwargs={'chat_id': '<id>'},
                         schema='UserSchema',
                         type_='user')

    prompt = Relationship(self_view='chat_prompt',
                          self_view_kwargs={'id': '<id>'},
                          related_view='prompt_detail',
                          related_view_kwargs={'chat_id': '<id>'},
                          schema='PromptSchema',
                          type_='prompt')

    messages = Relationship(self_view='chat_messages',
                            self_view_kwargs={'id': '<id>'},
                            related_view='message_list',
                            related_view_kwargs={'chat_id': '<id>'},
                            many=True,
                            schema='MessageSchema',
                            type_='message')


class MessageSchema(Schema):
    class Meta:
        type_ = 'message'
        self_view = 'message_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'message_list'
        inflect = underscore_to_camel

    id = fields.Integer(as_string=True, dump_only=True)
    date_created = fields.DateTime(dump_only=True)

    sender = fields.Str(dump_only=True)
    bot = fields.Bool()
    text = fields.Str()

    prompt = Relationship(self_view='message_prompt',
                          self_view_kwargs={'id': '<id>'},
                          related_view='prompt_detail',
                          related_view_kwargs={'message_id': '<id>'},
                          schema='PromptSchema',
                          type_='prompt')

    chat = Relationship(self_view='message_chat',
                        self_view_kwargs={'id': '<id>'},
                        related_view='chat_detail',
                        related_view_kwargs={'message_id': '<id>'},
                        schema='ChatSchema',
                        type_='chat')
