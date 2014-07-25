from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId

class LoginUserHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        # not allowed to use get on /users/login
        self.send_error(405)

    @gen.coroutine
    def post(self):
        search = {
            "email": self.get_argument("email"),
            "password": self.get_argument("password"),
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