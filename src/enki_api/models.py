import json
from datetime import datetime

from .database import db


class BaseModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    date_modified = db.Column(db.DateTime, nullable=True)
    private = db.Column(db.Boolean, default=True)

    @property
    def date_last_active(self):
        return self.date_modified or self.date_created

    def __repr__(self):
        return f'<{self.__class__.__name__} #{self.id}>'


class UserAsset(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class MessagesAsset(UserAsset):
    _messages = db.Column(db.Text, nullable=False)

    @property
    def messages(self):
        if self._messages == '[]':
            return []  # json.loads throws error on empty list
        return json.loads(self._messages)

    @messages.setter
    def messages(self, message_list):
        self._messages = json.dumps(message_list)


class Prompt(UserAsset):
    id = db.Column(db.Integer, primary_key=True)

    chats = db.relationship('Chat', backref=db.backref('prompt', lazy=True))

    name = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)

    intro_text = db.Column(db.Text, nullable=False)
    bot_name = db.Column(db.String(255), nullable=False)
    human_name = db.Column(db.String(255), nullable=False)
    max_tokens = db.Column(db.Integer, nullable=False)
    temperature = db.Column(db.Float(2), nullable=False)
    frequency_penalty = db.Column(db.Float(2), nullable=False)
    presence_penalty = db.Column(db.Float(2), nullable=False)


class Chat(UserAsset):
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'), nullable=False)


class User(BaseModel):
    username = db.Column(db.String(120), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    prompts = db.relationship('Prompt', backref=db.backref('user', lazy=True))
    chats = db.relationship('Chat', backref=db.backref('user', lazy=True))

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def display_name(self):
        return self.username or f'Anonymous #{self.id}'

    @property
    def assets_last_active(self):
        last_chat = sorted(self.chats, key=lambda c: c.date_last_active, reverse=True)[0]
        last_prompt = sorted(self.prompts, key=lambda p: p.date_last_active, reverse=True)[0]
        return {
            'prompt': last_prompt,
            'chat': last_chat
        }
