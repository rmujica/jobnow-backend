import os

from tornado.ioloop import IOLoop
from tornado.web import Application, url
import motor

# v2
import v2.handlers.index.index
import v2.handlers.users.user
import v2.handlers.users.search
import v2.handlers.users.login
import v2.handlers.users.message
import v2.handlers.offers.offer
import v2.handlers.offers.apply
import v2.handlers.offers.search
import v2.handlers.offers.reports

# system routes
routes = [
    # v2
    url(r"/v2/", v2.handlers.index.index.IndexHandler),
    url(r"/v2/users", v2.handlers.users.user.UserHandler),
    url(r"/v2/users/login", v2.handlers.users.login.LoginUserHandler),
    url(r"/v2/users/(\w+)", v2.handlers.users.search.SearchUserHandler),
    url(r"/v2/users/(\w+)/(\w+)", v2.handlers.users.message.MessageHandler),
    url(r"/v2/offers", v2.handlers.offers.offer.OfferHandler),
    url(r"/v2/offers/(\w+)", v2.handlers.offers.search.SearchOfferHandler),
    url(r"/v2/offers/(\w+)/applications", v2.handlers.offers.apply.ApplyOfferHandler),
    url(r"/v2/offers/(\w+)/applications/(\w+)", v2.handlers.offers.apply.ReviewOfferHandler),
    url(r"/v2/offers/(\w+)/reports", v2.handlers.offers.reports.ReportsHandler),
]

# mongo init
MONGO_URL = os.environ.get('MONGOHQ_URL')
DB_NAME = MONGO_URL.split("/")[-1]

application = Application(
    routes,
    db=motor.MotorClient(MONGO_URL)[DB_NAME],
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.listen(port)
    IOLoop.current().start()