from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship


class BaseSchema(Schema):
    id = fields.Integer(as_string=True, dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime()
    private = fields.Bool()
    date_last_active = fields.Function(lambda obj: obj.date_modified or obj.date_created)


class AssetSchema(BaseSchema):
    name = fields.Str()
    description = fields.Str()
    messages = fields.List(fields.List(fields.Str()))


class UserSchema(BaseSchema):
    class Meta:
        type_ = 'user'
        self_view = 'user_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'user_list'

    # TODO move assets_last_active here?
    email = fields.Email(load_only=True)
    username = fields.Str()
    display_name = fields.Function(lambda obj: obj.username or f'Anonymous #{obj.id}')
    prompts = Relationship(self_view='user_prompts',
                           self_view_kwargs={'id': '<id>'},
                           related_view='prompt_list',
                           related_view_kwargs={'id': '<id>'},
                           many=True,
                           schema='PromptSchema',
                           type_='prompt')


class PromptSchema(AssetSchema):
    class Meta:
        type_ = 'prompt'
        self_view = 'prompt_detail'
        self_view_kwargs = {'id': '<id>'}

    # TODO validation should probably go in here
    intro_text = fields.Str()
    bot_name = fields.Str()
    human_name = fields.Str()
    max_tokens = fields.Int()
    temperature = fields.Float()
    frequency_penalty = fields.Float()
    presence_penalty = fields.Float()
    owner = Relationship(attribute='user',
                         self_view='prompt_user',
                         self_view_kwargs={'id': '<id>'},
                         related_view='user_detail',
                         related_view_kwargs={'prompt_id': '<id>'},
                         schema='UserSchema',
                         type_='user')


class ChatSchema(AssetSchema):
    class Meta:
        type_ = 'chat'
        self_view = 'chat_detail'
        self_view_kwargs = {'id': '<id>'}

    prompt = Relationship(attribute='prompt',
                          self_view='chat_prompt',
                          self_view_kwargs={'id': '<id>'},
                          related_view='prompt_detail',
                          related_view_kwargs={'prompt_id': '<id>'},
                          schema='PromptSchema',
                          type_='prompt')

    owner = Relationship(attribute='user',
                         self_view='chat_user',
                         self_view_kwargs={'id': '<id>'},
                         related_view='user_detail',
                         related_view_kwargs={'chat_id': '<id>'},
                         schema='UserSchema',
                         type_='user')
