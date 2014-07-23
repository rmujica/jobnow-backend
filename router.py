from tornado.ioloop import IOLoop
from tornado.web import Application, url
import motor
import os

import handlers.index
import handlers.users

# system routes
routes = [
    url(r"/", handlers.index.IndexHandler),
    url(r"/users/", handlers.users.CreateHandler),
]

application = Application(routes)

# mongo init
MONGO_URL = os.environ.get('MONGOHQ_URL')
DB_NAME = MONGO_URL.split("/")[-1]
application.db = motor.MotorClient(MONGO_URL)[DB_NAME]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.listen(port)
    IOLoop.current().start()