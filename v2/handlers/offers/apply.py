import json

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId

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
            return

        # check if user has application
        if offer_id in user["applications"]:
            self.send_error(413)
            return

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


    @gen.coroutine
    def get(self, oid):
        # query collection using uid
        db = self.settings["db"]
        users = list()
        ret = dict()
        
        # is valid uid?
        try:
            offer_id = ObjectId(oid)
        except InvalidId:
            self.send_error(400)
            return

        # do search
        cursor = db.users.find({
            "applications": {
                "$in": [offer_id]
            }
        })

        while (yield cursor.fetch_next):
            user = cursor.next_object()
            users.append(user)

        # return
        ret["result"] = users
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(ret, default=jsonhandler.jsonhandler))
        self.finish()

class ReviewOfferHandler(RequestHandler):
    @gen.coroutine
    def put(self, oid, uid):
        db = self.settings["db"]
        # verify oid and uid
        try:
            oid = ObjectId(oid)
            uid = ObjectId(uid)
        except InvalidId:
            self.send_error(400)
            return

        # check if offer exists
        offer = yield db.offers.find_one({"_id": oid})
        if offer is None:
            self.send_error(404)
            return

        # check if user exists
        user = yield db.users.find_one({"_id": uid})
        if user is None or user["type"] == "b":
            self.send_error(412)
            return

        # check if user has application
        if oid not in user["applications"]:
            self.send_error(413)
            return

        # check if user has been accepted or rejected yet
        try:
            if uid in offer["accepted"] or uid in offer["rejected"]:
                self.send_error(414)
                return
        except KeyError:
            pass

        # add offer to application
        application_result = yield db.offers.update({
            "_id": oid
        }, {"$push": {
                "accepted": uid
            },
            "$pull": {
                "candidates": uid
            }
        })

        # add status to user
        user_result = yield db.users.update({
            "_id": uid
        }, {"$push": {"accepted": oid},
            "$pull": {"applications": oid}})

        # get updated offer
        updated_offer = yield db.offers.find_one({"_id": oid})

        # return updated offer
        self.set_status(201)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(updated_offer, default=jsonhandler.jsonhandler))
        self.finish()

    @gen.coroutine
    def delete(self, oid, uid):
        db = self.settings["db"]
        # verify oid and uid
        try:
            oid = ObjectId(oid)
            uid = ObjectId(uid)
        except InvalidId:
            self.send_error(400)
            return

        # check if offer exists
        offer = yield db.offers.find_one({"_id": oid})
        if offer is None:
            self.send_error(404)
            return

        # check if user exists
        user = yield db.users.find_one({"_id": uid})
        if user is None or user["type"] == "b":
            self.send_error(412)
            return

        # check if user has application
        if oid not in user["applications"]:
            self.send_error(413)
            return

        # check if user has been accepted or rejected yet
        try:
            if uid in offer["accepted"] or uid in offer["rejected"]:
                self.send_error(414)
                return
        except KeyError:
            pass

        # add offer to application
        application_result = yield db.offers.update({
            "_id": oid
        }, {"$push": {
                "rejected": uid
            },
            "$pull": {
                "candidates": uid
            }
        })

        # add status to user
        user_result = yield db.users.update({
            "_id": uid
        }, {"$push": {"rejected": oid},
            "$pull": {"applications": oid}})

        # get updated offer
        updated_offer = yield db.offers.find_one({"_id": oid})

        # return updated offer
        self.set_status(201)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(updated_offer, default=jsonhandler.jsonhandler))
        self.finish()