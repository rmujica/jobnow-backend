import json

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId

import helpers.json as jsonhandler

class ApplyOfferHandler(RequestHandler):
    @gen.coroutine
    def post(self, oid):
        uid = self.get_argument("user_id")

        # query collection using uid
        db = self.settings["db"]
        
        # is valid uid?
        try:
            offer_id = ObjectId(oid)
            user_id = ObjectId(uid)
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

        # add candidate to offer
        candidate_result = yield db.offers.update({
            "_id": offer_id
        }, {
            "$push": {
                "candidates": user_id
            }
        })

        # add offer to application
        application_result = yield db.users.update({
            "_id": user_id
        }, {
            "$push": {
                "applications": offer_id
            }
        })

        # get updated offer
        updated_offer = yield db.offers.find_one({"_id": offer_id})

        # return updated offer
        self.set_status(201)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(updated_offer, default=jsonhandler.jsonhandler))
        self.finish()