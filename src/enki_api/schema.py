from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema


class BaseSchema(Schema):
    id = fields.Integer(as_string=True, dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime()
    private = fields.Boolean()
    date_last_active = fields.Function(lambda obj: obj.date_modified or obj.date_created)


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

