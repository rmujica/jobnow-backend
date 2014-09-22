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
        offer["user_id"]           = self.get_argument("user_id")
        offer["short_description"] = self.get_argument("short_description")
        offer["long_description"]  = self.get_argument("long_description") 
        offer["price"]             = self.get_argument("price")
        offer["price_type"]        = self.get_argument("price_type")
        offer["category"]          = self.get_argument("category")
        offer["candidates"]        = list()
        #offer["start_date"]        = # PARSE DATE datetime.strptime
        #offer["end_date"]

        # is valid user id?
        try:
            offer["user_id"] = ObjectId(offer["user_id"])
        except InvalidId:
            self.send_error(400)
            return

        # do extraction
        text = offer["short_description"] + ".\n" + offer["long_description"]
        rake = Rake("keywords/spanish.stop")
        offer["keywords"] = rake.run(text)

        # add new record to db
        db = self.settings["db"]
        _id = yield db.offers.insert(offer)

        # get created object
        offer = yield db.offers.find_one({"_id": _id})

        # return json
        self.set_status(201)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(offer, default=jsonhandler.jsonhandler))
        self.finish()

    @gen.coroutine
    def get(self):
        search = self.get_query_argument("q", default=None)
        uid = self.get_query_argument("u", default=None)
        offers = list()
        ret    = dict()
        db     = self.settings["db"]
        ret["search_terms"] = list()

        if search is None and uid is None:
            # get all offers
            cursor = db.offers.find()

            while (yield cursor.fetch_next):
                offer = cursor.next_object()
                offers.append(offer)
        elif search is not None:
            # create search terms
            ret["search_terms"].extend([term.strip() for term in search.split(",")])
            search_terms = [re.compile(".*"+term.strip()+".*") for term in search.split(",")]

            # do search
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
            
            # create search term
            ret["search_terms"].extend([user_id])

            # do search
            cursor = db.offers.find({
                "candidates": user_id
            })

            while (yield cursor.fetch_next):
                offer = cursor.next_object()
                offers.append(offer)

        # return offers
        ret["result"] = offers
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(ret, default=jsonhandler.jsonhandler))
        self.finish()

    def options(self):
        # allow localhost development
        self.set_status(200)
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.finish()