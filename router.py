import os

from tornado.ioloop import IOLoop
from tornado.web import Application, url
import motor

# v1
import v1.handlers.index.index
import v1.handlers.users.user
import v1.handlers.users.search
import v1.handlers.users.login
import v1.handlers.offers.offer
import v1.handlers.offers.apply
import v1.handlers.offers.search

# v2
import v2.handlers.index.index
import v2.handlers.users.user
import v2.handlers.users.search
import v2.handlers.users.login
import v2.handlers.offers.offer
import v2.handlers.offers.apply
import v2.handlers.offers.search

# v3
import v3.handlers.index.index
import v3.handlers.users.user
import v3.handlers.users.search
import v3.handlers.users.login
import v3.handlers.offers.offer
import v3.handlers.offers.apply
import v3.handlers.offers.search

# system routes
routes = [
    # v1
    url(r"/", v1.handlers.index.index.IndexHandler),
    url(r"/users", v1.handlers.users.user.UserHandler),
    url(r"/users/login", v1.handlers.users.login.LoginUserHandler),
    url(r"/users/(\w+)", v1.handlers.users.search.SearchUserHandler),
    url(r"/offers", v1.handlers.offers.offer.OfferHandler),
    url(r"/offers/(\w+)", v1.handlers.offers.search.SearchOfferHandler),
    url(r"/offers/(\w+)/applications", v1.handlers.offers.apply.ApplyOfferHandler),

    # v2
    url(r"/v2/", v2.handlers.index.index.IndexHandler),
    url(r"/v2/users", v2.handlers.users.user.UserHandler),
    url(r"/v2/users/login", v2.handlers.users.login.LoginUserHandler),
    url(r"/v2/users/(\w+)", v2.handlers.users.search.SearchUserHandler),
    url(r"/v2/offers", v2.handlers.offers.offer.OfferHandler),
    url(r"/v2/offers/(\w+)", v2.handlers.offers.search.SearchOfferHandler),
    url(r"/v2/offers/(\w+)/applications", v2.handlers.offers.apply.ApplyOfferHandler),

    # v3
    url(r"/v3/", v3.handlers.index.index.IndexHandler),
    url(r"/v3/users", v3.handlers.users.user.UserHandler),
    url(r"/v3/users/login", v3.handlers.users.login.LoginUserHandler),
    url(r"/v3/users/(\w+)", v3.handlers.users.search.SearchUserHandler),
    url(r"/v3/offers", v3.handlers.offers.offer.OfferHandler),
    url(r"/v3/offers/(\w+)", v3.handlers.offers.search.SearchOfferHandler),
    url(r"/v3/offers/(\w+)/applications", v3.handlers.offers.apply.ApplyOfferHandler),
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