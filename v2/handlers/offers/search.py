import json
import re

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
                "candidates": {
                    "$elemMatch": {user_id}
                    }
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
        self.set_status(200)
        # necesario para desarrollo en localhost
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.finish()