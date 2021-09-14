import json
from datetime import datetime

from .database import db


class BaseModel(db.Model):
    __tablename__ = 'base'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))

    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    date_modified = db.Column(db.DateTime, nullable=True)
    private = db.Column(db.Boolean, default=True)

    __mapper_args__ = {
        'polymorphic_identity': 'base',
        'polymorphic_on': type
    }

    def __repr__(self):
        return f'<{self.__class__.__name__} #{self.id}>'


class Asset(BaseModel):
    __tablename__ = 'asset'

    id = db.Column(db.Integer, db.ForeignKey('base.id'), primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    _messages = db.Column(db.Text, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'asset',
    }

    @property
    def messages(self):
        if self._messages == '[]':
            return []  # json.loads throws error on empty list
        return json.loads(self._messages)

    @messages.setter
    def messages(self, message_list):
        self._messages = json.dumps(message_list)


class User(BaseModel):
    __tablename__ = 'user'

    id = db.Column(db.Integer, db.ForeignKey('base.id'), primary_key=True)

    username = db.Column(db.String(120), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    prompts = db.relationship('Prompt', backref=db.backref('owner', lazy=True), foreign_keys=[Asset.owner_id])
    chats = db.relationship('Chat', backref=db.backref('owner', lazy=True), foreign_keys=[Asset.owner_id])

    __mapper_args__ = {
        'polymorphic_identity': 'user',
    }

    def __repr__(self):
        return f'<User "{self.display_name}">'

    @property
    def assets_last_active(self):
        last_chat = sorted(self.chats, key=lambda c: c.date_last_active, reverse=True)[0]
        last_prompt = sorted(self.prompts, key=lambda p: p.date_last_active, reverse=True)[0]
        return {
            'prompt': last_prompt,
            'chat': last_chat
        }


class Chat(Asset):
    __tablename__ = 'chat'

    id = db.Column(db.Integer, db.ForeignKey('asset.id'), primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'), nullable=False)

    # owner = db.relationship("User", backref=db.backref('chats', lazy=True), foreign_keys=[Asset.owner_id])
    # prompt = db.relationship("Prompt", backref=db.backref('chats', lazy=True), foreign_keys=[Prompt.id])


class Prompt(Asset):
    __tablename__ = 'prompt'

    id = db.Column(db.Integer, db.ForeignKey('asset.id'), primary_key=True)

    # GPT args
    intro_text = db.Column(db.Text, nullable=False)
    bot_name = db.Column(db.String(255), nullable=False)
    human_name = db.Column(db.String(255), nullable=False)
    max_tokens = db.Column(db.Integer, nullable=False, default=300)
    temperature = db.Column(db.Float(2), nullable=False, default=0.5)
    frequency_penalty = db.Column(db.Float(2), nullable=False, default=0.0)
    presence_penalty = db.Column(db.Float(2), nullable=False, default=0.0)

    # owner = db.relationship("User", backref=db.backref('prompts', lazy=True), foreign_keys=[Asset.owner_id])
    chats = db.relationship('Chat', backref=db.backref('prompt', lazy=True), foreign_keys=[Chat.prompt_id])

    __mapper_args__ = {
        'polymorphic_identity': 'prompt',
    }
