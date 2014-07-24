from tornado.web import RequestHandler
from tornado import gen

class CreateUserHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        # not allowed to use get on /users
        self.send_error(405)

    @gen.coroutine
    def post(self):
        user = dict()
        user["first_name"] = self.get_argument("first_name")
        user["last_name"]  = self.get_argument("last_name")
        user["born"]       = self.get_argument("born")
        user["email"]      = self.get_argument("email")

        # add new record to db
        db = self.settings["db"]
        result = yield db.users.insert(user)