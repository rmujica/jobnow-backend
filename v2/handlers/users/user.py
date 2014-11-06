import json

from tornado.web import RequestHandler
from tornado import gen

import helpers.json as jsonhandler

class UserHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        user = dict()
        user["type"]         = self.get_argument("type") # u == user, b == business
        user["email"]        = self.get_argument("email")
        user["password"]     = self.get_argument("password")
        user["applications"] = list()
        user["offers"]       = list()
        user["status"]       = 0
        user["rating"]       = 0
        user["ratings"]      = list()
        user["my_ratings"]   = list()

        search = {
            "email": user["email"],
        }

        # search if user exists
        db = self.settings["db"]
        search_result = yield db.users.find_one(search)
        
        if search_result is None:
            # add new record to db
            _id = yield db.users.insert(user)

            # return created json
            user = yield db.users.find_one({"_id": _id})

            self.set_status(201)
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(user, default=jsonhandler.jsonhandler))
            self.finish()
        else:
            self.send_error(412)
