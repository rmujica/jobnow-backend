from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId

class CreateUserHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        # not allowed to use get on /users
        self.send_error(405)

    @gen.coroutine
    def post(self):
        user = dict()
        user_type = self.get_argument("type")
        user["email"]    = self.get_argument("email")
        user["password"] = self.get_argument("password")
        if user_type == "u":
            user["first_name"] = self.get_argument("first_name")
            user["last_name"]  = self.get_argument("last_name")
            user["born"]       = self.get_argument("born")
        elif user_type == "b":
            user["name"]        = self.get_argument("name")
            user["business_id"] = self.get_argument("business_id")
            user["phone"]       = self.get_argument("phone")

        # add new record to db
        db = self.settings["db"]
        _id = yield db.users.insert(user)

        # return created json
        user = yield db.users.find_one({"_id": _id})
        user["_id"] = str(user["_id"])
        self.set_status(201)
        self.write(user)

        self.finish()