from tornado.web import RequestHandler
from tornado import gen

class IndexHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        self.send_error(404)