import json
import datetime

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId

import helpers.json as jsonhandler

class RatingsHandler(RequestHandler):
    @gen.coroutine
    def post(self, uid):
        rater_id = self.get_argument("user_id")
        offer_id = self.get_argument("offer_id")
        new_rating = self.get_argument("rating")

        # check if both users exist
        db = self.settings["db"]
        try:
            rater_id = ObjectId(rater_id)
            uid = ObjectId(uid)
            offer_id = ObjectId(offer_id)
        except InvalidId:
            self.send_error(401)
            return

        new_rating = float(new_rating)

        rated_user = yield db.users.find_one({"_id": uid})
        rater_user = yield db.users.find_one({"_id": rater_id})
        offer = yield db.offers.find_one({"_id": offer_id})

        rating = rated_user["rating"] if "rating" in rated_user else 0
        ratings = rated_user["ratings"] if "ratings" in rated_user else list()

        if not rater_user or not rated_user or not offer:
            print(rater_user)
            print(rated_user)
            print(offer)
            self.send_error(402)
            return

        # add rating!
        rated_user = yield db.users.update({"_id": uid}, {
            "$push": {
                "ratings": {
                    "rater_id": rater_id,
                    "offer_id": offer_id,
                    "rating": new_rating
                }
            },
            "$set": {
                "rating": rating*len(ratings)/(len(ratings)+1) + new_rating/(len(ratings)+1)
            }
        })

        my_rated_user = yield db.users.update({"_id": rater_id}, {
            "$push": {
                "my_ratings": {
                    "rated_id": uid,
                    "offer_id": offer_id,
                    "rating": new_rating
                }
            }
        })

        # return updated rating
        updated_user = yield db.users.find_one({"_id": uid})

        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(updated_user, default=jsonhandler.jsonhandler))
        self.finish()