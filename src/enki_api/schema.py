from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship


class BaseSchema(Schema):
    id = fields.Integer(as_string=True, dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime()
    private = fields.Bool()
    date_last_active = fields.Function(lambda obj: obj.date_modified or obj.date_created)


class BaseRelationship(Relationship):
    def __init__(self, *args, **kwargs):
        super().__init__(
            self_view_kwargs={'id': '<id>'},
        )


class AssetSchema(BaseSchema):
    name = fields.Str()
    description = fields.Str()
    messages = fields.List(fields.List(fields.Str()))


class AssetRelationship(BaseRelationship):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         related_view_kwargs={'id': '<id>'},
                         many=True,
                         **kwargs)


class OwnerRelationship(BaseRelationship):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         attribute='owner',
                         related_view='user_detail',
                         schema='UserSchema',
                         type_='user',
                         **kwargs)


class UserSchema(BaseSchema):
    class Meta:
        type_ = 'user'
        self_view = 'user_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'user_list'

    email = fields.Email(load_only=True)
    username = fields.Str()
    display_name = fields.Function(lambda obj: obj.username or f'Anonymous #{obj.id}')
    # TODO move assets_last_active here?
    prompts = AssetRelationship(self_view='user_prompts',
                                related_view='prompt_list',
                                schema='PromptSchema',
                                type_='prompt')


class PromptSchema(BaseSchema):
    class Meta:
        type_ = 'prompt'
        self_view = 'prompt_detail'
        self_view_kwargs = {'id': '<id>'}

    # TODO validation should probably go in here
    owner = OwnerRelationship(self_view='prompt_owner',
                              related_view_kwargs={'prompt_id': '<id>'})
    intro_text = fields.Str()
    bot_name = fields.Str()
    human_name = fields.Str()
    max_tokens = fields.Int()
    temperature = fields.Float()
    frequency_penalty = fields.Float()
    presence_penalty = fields.Float()
