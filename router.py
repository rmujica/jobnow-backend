from tornado.ioloop import IOLoop
from tornado.web import Application, url
import motor
import os

from handlers.index.index import IndexHandler
from handlers.users.create import CreateUserHandler
from handlers.users.read import ReadUserHandler

# system routes
routes = [
    url(r"/", IndexHandler),
    url(r"/users/", CreateUserHandler),
    url(r"/users/([0-9]+)", ReadUserHandler),
]

# mongo init
MONGO_URL = os.environ.get('MONGOHQ_URL')
DB_NAME = MONGO_URL.split("/")[-1]

application = Application(routes, db=motor.MotorClient(MONGO_URL)[DB_NAME])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.listen(port)
    IOLoop.current().start()