import json
import datetime

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

    @gen.coroutine
    def put(self, uid):
        ret = dict()
        user = dict()

        db = self.settings["db"]

        # validate uid
        try:
            _id = ObjectId(uid)
        except InvalidId:
            self.send_error(400)
            return

        # does user exist?
        existing_user = yield db.users.find_one({"_id": _id})
        if not existing_user:
            self.send_error(400)
            return

        if existing_user["type"] == "u": 
            user["first_name"] = self.get_argument("first_name", default=None)
            user["last_name"] = self.get_argument("last_name", default=None)
            user["birth_date"] = self.get_argument("birth_date", default=None)
            user["location"] = self.get_argument("location", default=None)
            user["occupation"] = self.get_argument("occupation", default=None)
            user["facebook_user"] = self.get_argument("facebook_user", default=None)
        elif existing_user["type"] == "b":
            user["business_name"] = self.get_argument("business_name", default=None)
            user["address"] = self.get_argument("address", default=None)
            user["phone"] = self.get_argument("phone", default=None)

        user["status"] = self.get_argument("status", default=None)

        updated_user = dict()
        for k, v in user.items():
            if v is not None:
                if k == "birth_date":
                    updated_user[k] = datetime.datetime.strptime(user[k], "%d/%m/%Y")
                else:
                    updated_user[k] = user[k]

        # do update
        result = yield db.users.update({"_id": _id}, {"$set": updated_user})

        # return offers
        ret["result"] = yield db.users.find_one({"_id": _id})
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(ret, default=jsonhandler.jsonhandler))
        self.finish()

