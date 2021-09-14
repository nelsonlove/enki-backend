from flask import Flask
from . import database


app = Flask(__name__)

app.config['SECRET_KEY'] = 'ultratopsecretkey'
app.config['DEBUG'] = True

database.init_app(app)


if __name__ == '__main__':
    app.run()
