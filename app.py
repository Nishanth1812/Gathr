import os
import eventlet
# Enable eventlet for Socket.IO
eventlet.monkey_patch()
from flask import Flask, render_template, session, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask_socketio import SocketIO
import stripe
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
CORS(app)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Initialize Socket.IO with proper configuration
socketio = SocketIO(app, 
                  cors_allowed_origins="*",
                  async_mode='eventlet',
                  logger=True,
                  engineio_logger=True)

mongo = PyMongo(app)
app.extensions['pymongo'] = mongo  # Make mongo accessible from socketio handlers

# Import handlers after initializing components
from stripe_webhook import handle_stripe_webhook
from tree_logic import init_tree_state, get_tree_state
from webrtc_server import setup_webrtc_handlers
from test_donation import setup_donation_handlers
from stripe_handlers import setup_stripe_handlers

# Initialize tree state on startup
with app.app_context():
    init_tree_state(mongo)

# Set up WebRTC event handlers
setup_webrtc_handlers(socketio, app)

# Set up test donation handlers
setup_donation_handlers(socketio)

# Set up Stripe handlers
setup_stripe_handlers(app)

@app.route('/')
def landing_page():
    return render_template('index.html')

@app.route('/broadcast')
def broadcast_page():
    return render_template('broadcast.html')

@app.route('/watch')
def watch_page():
    return render_template('watch.html', stripe_key=os.getenv("STRIPE_PUBLISHABLE_KEY"))

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    return handle_stripe_webhook(mongo, socketio)

@app.route('/tree-state')
def tree_state():
    state = get_tree_state(mongo.db)
    return jsonify(state)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)