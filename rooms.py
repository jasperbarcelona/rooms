import flask, flask.views
from flask import url_for, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
import os


app = flask.Flask(__name__)

db = SQLAlchemy(app)

SHORTCODE = "xxxx"


class Room(db.Model):
    STATUSES = {
        'OCCUPIED': 0,
        'UNOCCUPIED': 1,
    }
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    floor = db.Column(db.Integer(2))
    status = db.Column(db.Integer(1), default=lambda: Room.STATUSES['UNOCCUPIED'])

    def occupy(self):
        self.status = self.STATUSES['OCCUPIED']

    def unoccupy(self):
        self.status = self.STATUSES['UNOCCUPIED']


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(16))
    access_token = db.Column(db.String(255))


@app.route('/webhooks/globe')
def webhooks_globe():
    """Use this endpoint for Globe's notify_uri"""
    data = request.data
    # FIXME: Unsafe parsing
    message_data = data['inboundSMSMessageList']['inboundSMSMessage'][0]
    subscriber_number = message_data['senderAddress']
    message = message_data['message']

    # Get access_token so for this subscriber.
    user = User.query.filter_by(number=subscriber_numer).order_by(User.id.desc()).first()

    if not user:
        return "User is not subscribed."

    # Check if the room is available.

    message_options = {
        'message': "Hello",
        'subscriber_number': user.subscriber_number,
    }
    r = requests.post(
        'http://devapi.globelabs.com.ph/smsmessaging/v1/outbound/2158%s/requests' % SHORTCODE,
        data=message_options
    )

    # If status_code is 200, then the message was sent.
    print r.status_code

    return "Ok"


@app.route('/authentication/globe', methods=['POST'])
def authentications_globe():
    """Use this endpoint for Globe's redirect_uri"""
    user = User(
        access_token=request.data.get('access_token'),
        number=request.data.get('subsriber_numer')
    )
    db.session.add(user)
    db.session.commit()
    return "Ok"



if __name__ == '__main__':
    app.debug = True
    app.run(port=int(os.environ['PORT']), host='0.0.0.0')