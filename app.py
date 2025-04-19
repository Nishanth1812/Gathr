import os
from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from stripe_webhook import handle_stripe_webhook

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

@app.route('/')
def landing_page():
    return 'The webhook listener is running properly'

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    return handle_stripe_webhook(mongo)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
