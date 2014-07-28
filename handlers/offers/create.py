from tornado.web import RequestHandler
from tornado import gen

from keywords.rake import Rake

class CreateOfferHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        offer = dict()
        offer["business_name"] = self.get_argument("business_name")
        offer["offer_name"]    = self.get_argument("offer_name")
        offer["description"]   = self.get_argument("description") 
        offer["price"]         = self.get_argument("price")
        offer["price_details"] = self.get_argument("price_details")

        # do extraction
        text = offer["offer_name"] + " " + offer["description"]
        rake = Rake("keywords/spanish.stop")
        offer["keywords"] = rake.run(text)

        # add new record to db
        db = self.settings["db"]
        _id = yield db.offers.insert(offer)

        # return created json
        offer = yield db.offers.find_one({"_id": _id})
        offer["_id"] = str(offer["_id"])

        self.set_status(201)
        self.write(offer)
        self.finish()