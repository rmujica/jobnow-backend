import json

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId

import helpers.json as jsonhandler

class SearchUserHandler(RequestHandler):
    @gen.coroutine
    def get(self, uid):
        # query collection using uid
        db = self.settings["db"]
        
        # is valid uid?
        try:
            _id = ObjectId(uid)
        except InvalidId:
            self.send_error(400)
            return

        # do search
        user = yield db.users.find_one({"_id": _id})

        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(user, default=jsonhandler.jsonhandler))
        self.finish()