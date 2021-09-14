from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
    db.app = app
    db.init_app(app)
    db.create_all(app=app)
