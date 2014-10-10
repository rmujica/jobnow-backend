import json
import re
import datetime

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId

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
        offer["start_date"]        = datetime.datetime.strptime(self.get_argument("start_date"), "%d/%m/%Y")
        offer["end_date"]          = datetime.datetime.strptime(self.get_argument("end_date"), "%d/%m/%Y")
        offer["lat"]               = self.get_argument("lat")
        offer["lng"]               = self.get_argument("lng")
        offer["loc"] = [float(offer["lat"]), float(offer["lng"])]

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

        # add offer to user
        new_offer_result = yield db.users.update({
            "_id": offer["user_id"]
        }, {
            "$push": {
                "offers": _id
            }
        })

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
        n = self.get_query_argument("n", default=None)
        latlng = self.get_query_argument("l", default=None)
        lat = None
        lng = None
        if latlng is not None:
            lat, lng = latlng.split(",")
            lat = float(lat)
            lng = float(lng)

        offers = list()
        ret    = dict()
        db     = self.settings["db"]
        ret["search_terms"] = list()

        if n is not None:
            n = int(n)
            offer_ids = list()
            today = datetime.datetime.today()

            cursor = yield db.offers.aggregate([
                {"$match": {"end_date": {"$gte": today}}},
                {"$unwind": "$candidates"},
                {"$group": {"_id": "$_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": n}
            ])

            for result in cursor["result"]:
                offer_ids.append(result["_id"])

            cursor = db.offers.find({
                "_id": {
                    "$in": offer_ids
                }
            })

            while (yield cursor.fetch_next):
                offer = cursor.next_object()
                offers.append(offer)

        elif latlng is not None:
            cursor = db.offers.find({
                "loc": {
                    "$near": [lat, lng]
                }
            })

            while (yield cursor.fetch_next):
                offer = cursor.next_object()
                offers.append(offer)
            ret["search_terms"].extend([lat, lng])

        elif search is None and uid is None and n is None and latlng is None:
            # get all offers
            cursor = db.offers.find()

            while (yield cursor.fetch_next):
                offer = cursor.next_object()
                offers.append(offer)

            ret["search_terms"].extend(["all"])
        else:
            if search is not None:
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
                    
            if uid is not None:
                # is valid user id?
                try:
                    user_id = ObjectId(uid)
                except InvalidId:
                    self.send_error(400)
                    return
            
                # create search term
                ret["search_terms"].extend(user_id)

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