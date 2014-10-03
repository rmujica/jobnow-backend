import json
import re
import datetime

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId

from keywords.rake import Rake
import helpers.json as jsonhandler

class SearchOfferHandler(RequestHandler):
    @gen.coroutine
    def get(self, user):
        search = self.get_query_argument("q", default=None)
        uid = self.get_query_argument("u", default=None)
        offers = list()
        ret = dict()
        db = self.settings["db"]

        if search is None and uid is None:
            # get all offers
            ret["search_terms"] = list()
            cursor = db.offers.find()
            
            while (yield cursor.fetch_next):
                offer = cursor.next_object()
                offers.append(offer)
        elif search is not None:
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
        elif uid is not None:
            # is valid user id?
            try:
                user_id = ObjectId(uid)
            except InvalidId:
                self.send_error(400)
                return
            cursor = db.offers.find({
                "candidates": user_id
            })
            while (yield cursor.fetch_next):
                offer = cursor.next_object()
                offers.append(offer)
            ret["search_terms"] = [user_id]

        # return offers
        ret["result"] = offers
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(ret, default=jsonhandler.jsonhandler))
        self.finish()

    @gen.coroutine
    def put(self, offer_id):
        ret = dict()
        offer = dict()
        offer["short_description"] = self.get_argument("short_description", default=None)
        offer["long_description"]  = self.get_argument("long_description", default=None) 
        offer["price"]             = self.get_argument("price", default=None)
        offer["price_type"]        = self.get_argument("price_type", default=None)
        offer["category"]          = self.get_argument("category", default=None)
        offer["start_date"]        = datetime.datetime.strptime(self.get_argument("start_date", default=None), "%d/%m/%Y")
        offer["end_date"]          = datetime.datetime.strptime(self.get_argument("end_date", default=None), "%d/%m/%Y")
        offer["lat"]               = self.get_argument("lat", default=None)
        offer["lng"]               = self.get_argument("lng", default=None)

        db = self.settings["db"]

        # verify offer id
        try:
            offer_id = ObjectId(offer_id)
        except InvalidId:
            self.send_error(400)
            return

        # what fields we update?
        for k, v in offer.items():
            if v is None:
                del offer[k]

        # do update
        offer["_id"] = offer_id
        result = yield db.offers.update(offer)

        # return offers
        ret["result"] = offer
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(ret, default=jsonhandler.jsonhandler))
        self.finish()

    def options(self):
        self.set_status(200)
        # necesario para desarrollo en localhost
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.finish()