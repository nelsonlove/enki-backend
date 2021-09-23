from sqlalchemy import update
from sqlalchemy.orm import declared_attr

from .database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.now())
    date_modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    auth_id = db.Column(db.String(120), unique=True, nullable=False)  # from auth0
    nickname = db.Column(db.String(120), unique=True, nullable=True)
    api_key = db.Column(db.String(80), nullable=True)

    visible_chats = db.Column(db.Boolean, default=False)
    visible_prompts = db.Column(db.Boolean, default=True)

    def touch(self):
        db.engine.execute(
            update(User).where(User.id == self.id)
        )

    def __repr__(self):
        return f'<User #{self.id}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.now())

    prompt = db.relationship('Prompt', backref=db.backref('messages', lazy=True))
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'), nullable=True)

    chat = db.relationship('Chat', backref=db.backref('messages', lazy=True))
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=True)

    bot = db.Column(db.Boolean)
    text = db.Column(db.Text, nullable=False)

    @property
    def sender(self):
        if self.prompt_id:
            prompt = self.prompt
        else:
            prompt = self.chat.prompt
        if self.bot:
            return prompt.bot
        else:
            return prompt.human

    def check_if_needs_reply(self):
        if self.chat and not self.bot:
            self.chat.get_reply()

    def __repr__(self):
        return f'<Message #{self.id} [{self.sender}: {self.text}]>'


class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.now())
    date_modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    visible = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    intro = db.Column(db.Text, nullable=False)
    bot = db.Column(db.String(255), nullable=False)
    human = db.Column(db.String(255), nullable=False)

    temperature = db.Column(db.Integer, nullable=False, default=50)
    variety = db.Column(db.Integer, nullable=False, default=50)
    verbosity = db.Column(db.Integer, nullable=False, default=300)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref=db.backref('prompts', lazy=True))

    def __repr__(self):
        return f'<Prompt #{self.id}>'


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.now())
    date_modified = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    visible = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    owner = db.relationship("User", backref=db.backref('chats', lazy=True))

    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'), nullable=True)
    prompt = db.relationship("Prompt", backref=db.backref('chats', lazy=True))

    def __repr__(self):
        return f'<Chat #{self.id}>'

    owner = db.relationship('User', backref=db.backref('prompts'))


class User(BaseModel):
    nickname = db.Column(db.String(120), unique=True, nullable=True)
    auth_id = db.Column(db.String(120), unique=True, nullable=False)  # from auth0
    api_key = db.Column(db.String(80), unique=True, nullable=False)

    def touch(self):
        stmt = update(User).where(User.id == self.id)
        db.engine.execute(stmt)

    @property
    def assets_last_active(self):
        last_chat = sorted(self.chats, key=lambda c: c.date_last_active, reverse=True)[0]
        last_prompt = sorted(self.prompts, key=lambda p: p.date_last_active, reverse=True)[0]
        return {
            'prompt': last_prompt,
            'chat': last_chat
        }
