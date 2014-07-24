from tornado.web import RequestHandler
from tornado import gen

class ReadUserHandler(RequestHandler):
    @gen.coroutine
    def get(self, id):
        # query collection using id
        db = self.settings["db"]
        user = yield db.users.find_one({"_id": id})
        user = user if user else "{}"
        self.write(user)

    @gen.coroutine
    def post(self, id):
        # not allowed to use get on /users/(id)
        self.send_error(405)