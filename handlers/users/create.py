from tornado.web import RequestHandler
from tornado import gen

class CreateUserHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        user = dict()
        user["type"]     = self.get_argument("type") # u == user, b == business
        user["email"]    = self.get_argument("email")
        user["password"] = self.get_argument("password")

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
            user["_id"] = str(user["_id"])
            self.set_status(201)
            self.write(user)

            self.finish()
        else:
            # 404: resource not found
            self.send_error(404)