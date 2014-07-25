from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId

class CreateOfferHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        # not allowed to use get on /offers
        self.send_error(405)

    @gen.coroutine
    def post(self):
        offer = dict()
        offer["business_name"] = self.get_argument("business_name")
        offer["offer_name"]  = self.get_argument("offer_name")
        offer["description"]       = self.get_argument("description")
        try:
            offer["price"]       = int(self.get_argument("price"))
        except ValueError:
            self.send_error(400)
        offer["price_details"] = self.get_argument("price_details")
        

        # add new record to db
        db = self.settings["db"]
        _id = yield db.offers.insert(offer)

        # return created json
        offer = yield db.offers.find_one({"_id": _id})
        offer["_id"] = str(offers["_id"])
        self.set_status(201)
        self.write(offers)

        self.finish()
