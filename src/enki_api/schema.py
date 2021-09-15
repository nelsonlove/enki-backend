from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship


class BaseSchema(Schema):
    id = fields.Integer(as_string=True, dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime()
    private = fields.Bool()


class AssetSchema(BaseSchema):
    name = fields.Str()
    description = fields.Str()


class UserSchema(BaseSchema):
    class Meta:
        type_ = 'user'
        self_view = 'user_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'user_list'

    # TODO move assets_last_active here?
    auth_id = fields.Str()  # from auth0
    username = fields.Str()
    display_name = fields.Function(lambda obj: obj.username or f'Anonymous #{obj.id}')
    prompts = Relationship(self_view='user_prompts',
                           self_view_kwargs={'id': '<id>'},
                           related_view='prompt_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='PromptSchema',
                           type_='prompt')
    chats = Relationship(self_view='user_chats',
                         self_view_kwargs={'id': '<id>'},
                         related_view='chat_list',
                         related_view_kwargs={'id': '<id>'},
                         many=True,
                         schema='ChatSchema',
                         type_='chat')


class PromptSchema(AssetSchema):
    class Meta:
        type_ = 'prompt'
        self_view = 'prompt_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'prompt_list'

    # TODO validation should probably go in here
    intro_text = fields.Str()
    bot_name = fields.Str()
    human_name = fields.Str()
    max_tokens = fields.Int()
    temperature = fields.Float()
    frequency_penalty = fields.Float()
    presence_penalty = fields.Float()
    messages = fields.List(fields.List(fields.Str()))
    owner = Relationship(self_view='prompt_user',
                         self_view_kwargs={'id': '<id>'},
                         related_view='user_detail',
                         related_view_kwargs={'prompt_id': '<id>'},
                         schema='UserSchema',
                         type_='user')
    chats = Relationship(self_view='prompt_chats',
                         self_view_kwargs={'id': '<id>'},
                         related_view='chat_list',
                         related_view_kwargs={'chat_id': '<id>'},
                         many=True,
                         schema='ChatSchema',
                         type_='chat')


class ChatSchema(AssetSchema):
    class Meta:
        type_ = 'chat'
        self_view = 'chat_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'chat_list'

    messages = fields.Function(lambda obj: obj.prompt.messages + obj.messages)
    owner = Relationship(self_view='chat_user',
                         self_view_kwargs={'id': '<id>'},
                         related_view='user_detail',
                         related_view_kwargs={'chat_id': '<id>'},
                         schema='UserSchema',
                         type_='user')
    prompt = Relationship(self_view='chat_prompt',
                          self_view_kwargs={'id': '<id>'},
                          related_view='prompt_detail',
                          related_view_kwargs={'id': '<id>'},
                          schema='PromptSchema',
                          type_='prompt')
