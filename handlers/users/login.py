from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId

class ReadUserHandler(RequestHandler):
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
        if user is None:
            user = {}
        else:
            user["_id"] = str(user["_id"])
        self.write(user)
        self.finish()

    @gen.coroutine
    def post(self, uid):
        search = {
            "email": self.get_argument("email")
            "password": self.get_argument("password")
        }

        # search using login data
        user = yield db.users.find_one(search)
        if user is None:
            # 404: resource not found
            self.send_error(404)
        else:
            user["_id"] = str(user["_id"])
            self.write(user)
            self.finish()