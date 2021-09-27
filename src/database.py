from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init(app, dev=True):
    dev_config = {
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///sqlite.db',
    }
    prod_config = {
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_DATABASE_URI': ('mysql+pymysql://'
                                    # TODO totally insecure change this to env variable
                                    'nelson:colorlessgreenideassleepfuriously'
                                    '@mydbinstance.c9belejmkhsm.us-east-1.rds.amazonaws.com'
                                    '/db'
                                    '?ssl_ca=/users/nelson/Downloads/us-east-1-bundle.pem'
                                    )
    }
    config = dev_config if dev else prod_config
    for key, value in config.items():
        app.config[key] = value

    db.app = app
    db.init_app(app)
    db.create_all(app=app)
