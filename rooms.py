import flask, flask.views
from flask import url_for, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import os
import requests


app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

SHORTCODE = "9903"
SMS_URL = "http://devapi.globelabs.com.ph/smsmessaging/v1/outbound/%s/requests"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    section = db.Column(db.String(7))
    number = db.Column(db.String(30))
    access_token = db.Column(db.String(255))

    @property
    def parsed_number(self):
        return self.number[7:]


@app.route('/webhooks/globe', methods=['GET', 'POST'])
def webhooks_globe():
    """Use this endpoint for Globe's notify_uri"""
    data = request.json
    a = User.query.all()
    print "xxxxxxxx"
    print a[0].number
    print "xxxxxxxx"
    # FIXME: Unsafe parsing
    print data
    message_data = data['inboundSMSMessageList']['inboundSMSMessage'][0]
    subscriber_number = message_data['senderAddress']
    message = message_data['message']

    print subscriber_number
    print message

    if message[:3] == 'all':
        recipient = "all"
        sendThis = message[4:]
        user = User.query.all()
    else:
        recipient = message[:7]
        sendThis = message[8:]
        user = User.query.filter_by(section=recipient).all()
    # Get access_token so for this subscriber.
    

    for x in range (0,len(user)):
        message_options = {
            "message": sendThis,
            "address": user[x].parsed_number,
            "access_token": user[x].access_token,
        }

        print message_options
        r = requests.post(
            SMS_URL % SHORTCODE,
            params=message_options
        )

    # If status_code is 200, then the message was sent.
    print SMS_URL % SHORTCODE
    print r.status_code
    print r.text
    return "Ok"


@app.route('/authentication/globe', methods=['GET', 'POST'])
def authentications_globe():
    """Use this endpoint for Globe's redirect_uri"""

    print request.args
    user = User.query.filter_by(number="tel:+63" + request.args['subscriber_number'])

    if user:
        user.access_token=request.args['access_token']

    db.session.commit()
    return "Ok"


@app.route('/db/rebuild')
def db_rebuild():
    db.drop_all()
    db.create_all()
    a = User(number='09183339068')
    db.session.add(a)
    db.session.commit()
    return "ok"


if __name__ == '__main__':
    app.debug = True
    app.run(port=int(os.environ['PORT']), host='0.0.0.0')