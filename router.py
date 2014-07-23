from tornado.ioloop import IOLoop
from tornado.web import Application, url
import motor
import os

import handlers.index

# system routes
routes = [
    url(r"/", handlers.index.IndexHandler),
]

application = Application(routes)
application.db = None

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.listen(port)
    IOLoop.current().start()