from tornado.web import RequestHandler
from tornado import gen

class CreateHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        # not allowed to use get on /users
        self.send_error(405)

    @gen.coroutine
    def post(self):
        first_name = self.get_argument("first_name")
        last_name  = self.get_argument("last_name")
        born       = self.get_argument("born")
        email      = self.get_argument("email")

        # add new record to db