import json

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId

import helpers.json as jsonhandler

class ReportsHandler(RequestHandler):
    @gen.coroutine
    def post(self, oid):
        reporting_user = self.get_argument("user_id")
        report_text = self.get_argument("message")

        db = self.settings["db"]

        try:
            user_id = ObjectId(reporting_user)
            offer_id = ObjectId(oid)
        except InvalidId:
            self.send_error(400)
            return

        # check if offer exists
        offer = yield db.offers.find_one({"_id": offer_id})
        if offer is None:
            self.send_error(404)
            return

        # check if user exists
        user = yield db.users.find_one({"_id": user_id})
        if user is None or user["type"] == "b":
            self.send_error(412)
            return

        # add report to offer
        report["user_id"] = user_id
        report["message"] = report_text
        offer_update = yield db.offers.update({
            "_id": offer_id
        }, {
            "$push": {
                "reports": report
            }
        })

        # get updated offer
        updated_offer = yield db.offers.find_one({"_id": offer_id})

        # return updated offer
        self.set_status(201)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(updated_offer, default=jsonhandler.jsonhandler))
        self.finish()