import json

from sqlalchemy.orm import declared_attr

from .database import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    date_created = db.Column(db.DateTime, default=db.func.now())
    date_modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    private = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<{self.__class__.__name__} #{self.id}>'


class Asset(BaseModel):
    __abstract__ = True

    name = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    _messages = db.Column(db.Text, nullable=False)

    @declared_attr
    def owner_id(cls):
        return db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def messages(self):
        if self._messages == '[]':
            return []  # json.loads throws error on empty list
        return json.loads(self._messages)

    @messages.setter
    def messages(self, message_list):
        self._messages = json.dumps(message_list)


class Chat(Asset):
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'), nullable=False)

    owner = db.relationship("User", backref=db.backref('chats', lazy=True))
    prompt = db.relationship("Prompt", backref=db.backref('chats', lazy=True))


class Prompt(Asset):
    # GPT args
    intro_text = db.Column(db.Text, nullable=False)
    bot_name = db.Column(db.String(255), nullable=False)
    human_name = db.Column(db.String(255), nullable=False)
    max_tokens = db.Column(db.Integer, nullable=False, default=300)
    temperature = db.Column(db.Float(2), nullable=False, default=0.5)
    frequency_penalty = db.Column(db.Float(2), nullable=False, default=0.0)
    presence_penalty = db.Column(db.Float(2), nullable=False, default=0.0)

    owner = db.relationship('User', backref=db.backref('prompts'))


class User(BaseModel):
    username = db.Column(db.String(120), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api_key = db.Column(db.String(80), unique=True, nullable=False)

    @property
    def assets_last_active(self):
        last_chat = sorted(self.chats, key=lambda c: c.date_last_active, reverse=True)[0]
        last_prompt = sorted(self.prompts, key=lambda p: p.date_last_active, reverse=True)[0]
        return {
            'prompt': last_prompt,
            'chat': last_chat
        }
