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
        offers = list()
        ret = dict()
        db = self.settings["db"]

        # todo: use USER !!!!

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