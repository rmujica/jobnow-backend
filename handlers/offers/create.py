from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId

class CreateOfferHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        # not allowed to use get on /offers
        self.send_error(405)

    @gen.coroutine
    def post(self):
        user = dict()
        user["first_name"] = self.get_argument("first_name")
        user["last_name"]  = self.get_argument("last_name")
        user["born"]       = self.get_argument("born")
        user["email"]      = self.get_argument("email")
        user["password"]   = self.get_argument("password")

        # add new record to db
        db = self.settings["db"]
        _id = yield db.users.insert(user)

        # return created json
        user = yield db.users.find_one({"_id": _id})
        user["_id"] = str(user["_id"])
        self.set_status(201)
        self.write(user)

        self.finish()