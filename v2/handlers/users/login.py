import json

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId

import helpers.json as jsonhandler

class LoginUserHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        search = {
            "email": self.get_argument("email"),
            "password": self.get_argument("password"),
        }

        # search using login data
        db = self.settings["db"]
        user = yield db.users.find_one(search)

        # user exists?
        #if user is None:
        #    self.send_error(404)
        #else:
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(user, default=jsonhandler.jsonhandler))
        self.finish()