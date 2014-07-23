from tornado.ioloop import IOLoop
from tornado.web import Application, url
import motor

import handlers.index

# system routes
routes = [
    url(r"/", handlers.index.IndexHandler),
]

application = Application(routes)
application.db = None

if __name__ == "__main__":  
    application.listen(8888)
    IOLoop.current().start()