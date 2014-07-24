from tornado.web import RequestHandler
from tornado import gen

class ReadUserHandler(RequestHandler):
    @gen.coroutine
    def get(self, uid):
        # query collection using uid
        db = self.settings["db"]
        user = yield db.users.find_one({"_id": uid})
        self.write(user)

    @gen.coroutine
    def post(self, uid):
        # not allowed to use get on /users/(uid)
        self.send_error(405)