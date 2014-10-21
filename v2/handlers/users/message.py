import os
import smtplib

from tornado.web import RequestHandler
from tornado import gen
from bson.objectid import ObjectId
from bson.errors import InvalidId
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import helpers.json as jsonhandler

class MessageHandler(RequestHandler):
    @gen.coroutine
    def post(self, from_uid, to_uid):
        message = self.get_argument("message", default="holiwi")

        # verify users id
        try:
            from_uid = ObjectId(from_id)
            to_uid = ObjectId(to_id)
        except InvalidId:
            self.send_error(400)
            return

        # get user data
        db = self.settings["db"]
        from_user = yield db.users.find_one({"_id": from_uid})
        to_user = yield db.users.find_one({"_id": to_uid})

        # create email TODO as async
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "jobnow message"
        msg["From"] = from_user["email"]
        msg["To"] = to_user["email"]
        text = "<p>Hola loquillo</p>"
        text += "<p>" + from_user["username"] + "se tiro un peo en tu cara</p>"
        part1 = MIMEText(text, "html")
        username = os.environ["MANDRILL_USERNAME"]
        password = os.environ["MANDRILL_APIKEY"]
        msg.attach(part1)
        s = smtplib.SMTP("smtp.mandrillapp.com", 587)
        s.login(username, password)
        s.sendmail(msg["From"], msg["To"], msg.as_string())
        s.quit()

        self.set_status(201)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({"msg": msg.as_string()}, default=jsonhandler.jsonhandler))
        self.finish()