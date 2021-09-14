from flask import Flask
import database


app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'

database.init_app(app)


if __name__ == '__main__':
    app.run()
