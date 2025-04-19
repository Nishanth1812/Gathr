import os
import stripe
from flask import request, jsonify
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret_key = os.getenv("STRIPE_WEBHOOK_SECRET")

def handle_stripe_webhook(mongo):
    payload = request.data
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret_key)
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event['type'] == 'checkout.session.completed':
        cust_data = event['data']['object']
        intent = stripe.PaymentIntent.retrieve(cust_data['payment_intent'])

        mongo.db.donor_data.insert_one({
            "name": cust_data.get('customer_details', {}).get('name', 'Anonymous'),
            "email": cust_data.get('customer_details', {}).get('email', 'anonymous@example.com'),
            "amount": intent.amount_received / 100,
            "timestamp": datetime.fromtimestamp(intent.created, tz=timezone.utc)
        })

    return jsonify(success=True), 200