import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, send_file
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from stripe_webhook import handle_stripe_webhook
from socket_handle import socketio,init_s
load_dotenv()

app = Flask(__name__)
init_s(app)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

@app.route('/')

def serve_test_page():
    return send_file('test.html')

def landing_page():
    return 'The webhook listener is running properly'

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    return handle_stripe_webhook(mongo)

if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi
    eventlet.monkey_patch()
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
