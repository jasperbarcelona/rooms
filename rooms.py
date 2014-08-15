import flask, flask.views
from flask import url_for, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
import os
import requests


app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

SHORTCODE = "9903"


class Room(db.Model):
    STATUSES = {
        'OCCUPIED': 0,
        'UNOCCUPIED': 1,
    }
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    floor = db.Column(db.Integer())
    status = db.Column(db.Integer(), default=lambda: Room.STATUSES['UNOCCUPIED'])

    def occupy(self):
        self.status = self.STATUSES['OCCUPIED']

    def unoccupy(self):
        self.status = self.STATUSES['UNOCCUPIED']


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(30))
    access_token = db.Column(db.String(255))


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

    # Get access_token so for this subscriber.
    user = User.query.filter_by(number=subscriber_number).order_by(User.id.desc()).first()

    message_options = {
        "clientCorrelator": '123456',
        "senderAddress": SHORTCODE,
        "outboundSMSTextMessage": "Hello",
        "address": subscriber_number,
    }

    r = requests.post(
        'http://devapi.globelabs.com.ph/smsmessaging/v1/outbound/%s/requests?access_token=' % (SHORTCODE, user.access_token),
        data=message_options
    )

    # If status_code is 200, then the message was sent.
    print r.status_code

    return "Ok"


@app.route('/authentication/globe', methods=['GET', 'POST'])
def authentications_globe():
    """Use this endpoint for Globe's redirect_uri"""

    print request.args
    user = User(number="tel:+63" + request.args['subscriber_number'], access_token=request.args['access_token'])
    db.session.add(user)
    print user.number
    print user.access_token
    db.session.commit()
    return "Ok"


@app.route('/db/rebuild')
def db_rebuild():
    db.drop_all()
    db.create_all()
    return os.environ['DATABASE_URL']


if __name__ == '__main__':
    app.debug = True
    app.run(port=int(os.environ['PORT']), host='0.0.0.0')