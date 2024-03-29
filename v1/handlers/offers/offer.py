import json
import re

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId

from keywords.rake import Rake
import helpers.json as jsonhandler

class OfferHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        offer = dict()
        offer["business_name"] = self.get_argument("business_name")
        offer["offer_name"]    = self.get_argument("offer_name")
        offer["description"]   = self.get_argument("description") 
        offer["price"]         = self.get_argument("price")
        offer["price_details"] = self.get_argument("price_details")
        offer["user_id"]       = self.get_argument("user_id", default=None)

        # is valid user id?
        try:
            offer["user_id"] = ObjectId(offer["user_id"])
        except InvalidId:
            self.send_error(400)
            return

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

    @gen.coroutine
    def get(self):
        search = self.get_query_argument("q", default=None)
        offers = list()
        ret = dict()
        db = self.settings["db"]

        if search is None:
            # get all offers
            cursor = db.offers.find()
            while (yield cursor.fetch_next):
                offer = cursor.next_object()
                offers.append(offer)
        else:
            # do search
            search_terms = [re.compile(".*"+term.strip()+".*") for term in search.split(",")]
            ret["search_terms"] = [term.strip() for term in search.split(",")]
            cursor = db.offers.find({
                "keywords.keyword": {
                    "$in": search_terms
                    }
                })
            while (yield cursor.fetch_next):
                offer = cursor.next_object()
                offers.append(offer)

        # return offers
        ret["result"] = offers
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        # necesario para desarrollo en localhost
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(json.dumps(ret, default=jsonhandler.jsonhandler))
        self.finish()

    def options(self):
        self.set_status(200)
        # necesario para desarrollo en localhost
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.finish()