import json

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId

import helpers.json as jsonhandler

class ReportsHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        # get all reports
        db = self.settings["db"]

        cursor = db.offers.find({"reports.1": {"$exists": True}})
        ret = dict()
        ret["result"] = list()
        while (yield cursor.fetch_next):
            result = cursor.next_object()
            ret["result"].append(result)

        # return updated offer
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(ret, default=jsonhandler.jsonhandler))
        self.finish()