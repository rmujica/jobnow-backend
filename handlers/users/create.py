from tornado.web import RequestHandler
from tornado import gen

class CreateUserHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        user = dict()
        user["type"]     = self.get_argument("type") # u == user, b == business
        user["email"]    = self.get_argument("email")
        user["password"] = self.get_argument("password")
        if user["type"] == "u":
            user["first_name"] = self.get_argument("first_name")
            user["last_name"]  = self.get_argument("last_name")
            user["born"]       = self.get_argument("born")
        elif user["type"] == "b":
            user["name"]        = self.get_argument("name")
            user["business_id"] = self.get_argument("business_id")
            user["phone"]       = self.get_argument("phone")

        search = {
            "email": user["email"],
        }

        print(user["email"])
        print(user["password"])

        # search if user exists
        db = self.settings["db"]
        search_result = yield db.users.find_one(search)
        
        if search_result is None:
            # add new record to db
            _id = yield db.users.insert(user)

            # return created json
            user = yield db.users.find_one({"_id": _id})
            user["_id"] = str(user["_id"])
            self.set_status(201)
            self.write(user)

            self.finish()
        else:
            # 404: resource not found
            self.send_error(404)