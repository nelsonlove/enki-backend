from flask import Flask
from flask_rest_jsonapi import Api
from flask_cors import CORS

import database
import resource

application = app = Flask(__name__)

app.config['SECRET_KEY'] = 'ultratopsecretkey'
app.config['DEBUG'] = True

CORS(app)

db = database.db
database.init(app)

api = Api(app)

resource.UserList.add_routes(api)
resource.UserDetail.add_routes(api)
resource.UserRelationship.add_routes(api)

resource.PromptList.add_routes(api)
resource.PromptDetail.add_routes(api)
resource.PromptRelationship.add_routes(api)

resource.ChatList.add_routes(api)
resource.ChatDetail.add_routes(api)
resource.ChatRelationship.add_routes(api)

resource.MessageList.add_routes(api)
resource.MessageDetail.add_routes(api)
resource.MessageRelationship.add_routes(api)


if __name__ == '__main__':
    app.run()
