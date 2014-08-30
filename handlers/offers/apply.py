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
        except InvalidId:
            self.send_error(400)
            return

        # add application
        result = yield db.offers.update({
            "_id": oid
        }, {
            "$push": {
                "candidates": uid
            }
        })

        updated_offer = yield db.offers.find_one({"_id": oid})
        updated_offer["_id"] = str(updated_offer["_id"])

        self.set_status(201)
        self.write(updated_offer)
        self.finish()