import json
import re
import datetime

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId

from keywords.rake import Rake
import helpers.json as jsonhandler

class SearchOfferHandler(RequestHandler):
    @gen.coroutine
    def get(self, offer_id):
        db = self.settings["db"]

        # check offer id
        try:
            offer_id = ObjectId(offer_id)
        except InvalidId:
            self.send_error(400)
            return

        # do search
        offer = yield db.offers.find_one({"_id": offer_id})

        # return offers
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(offer, default=jsonhandler.jsonhandler))
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
        offer["start_date"]        = self.get_argument("start_date", default=None)
        offer["end_date"]          = self.get_argument("end_date", default=None)
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
        updated_offer = dict()
        for k, v in offer.items():
            if v is not None:
                if k == "start_date" or k == "end_date":
                    updated_offer[k] = datetime.datetime.strptime(offer[k], "%d/%m/%Y")
                else:
                    updated_offer[k] = offer[k]

        # do update
        result = yield db.offers.update({"_id": offer_id}, {"$set": updated_offer})

        # return offers
        ret["result"] = yield db.offers.find_one({"_id": offer_id})
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(ret, default=jsonhandler.jsonhandler))
        self.finish()

    @gen.coroutine
    def delete(self, offer_id):
        db = self.settings["db"]

        # verify offer id
        try:
            offer_id = ObjectId(offer_id)
        except InvalidId:
            self.send_error(400)
            return

        # do delete
        result = yield db.offers.remove({"_id": offer_id})

        # return offers
        ret["result"] = {}
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