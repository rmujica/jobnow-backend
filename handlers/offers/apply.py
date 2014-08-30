from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId

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

        offer = yield db.offers.find_one({"_id": offer_id})
        if offer is None:
            print("offer is: " + str(offer_id))
            self.send_error(404)
            return

        # add application
        result = yield db.offers.update({
            "_id": offer_id
        }, {
            "$push": {
                "candidates": user_id
            }
        })

        updated_offer = yield db.offers.find_one({"_id": offer_id})
        updated_offer["_id"] = str(updated_offer["_id"])

        self.set_status(201)
        self.write(updated_offer)
        self.finish()