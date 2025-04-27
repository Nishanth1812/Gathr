import stripe
from flask import request, jsonify
import os
from tree_logic import update_tree_on_donation

def handle_stripe_webhook(mongo, socketio):
    payload = request.data
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, 
            sig_header,
            webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify(error=str(e)), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify(error=str(e)), 400
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Extract donor information from metadata
        donor_name = session.get('metadata', {}).get('donor_name', 'Anonymous')
        amount = session.get('amount_total', 0) / 100  # Convert to dollars

        # Update tree with donation information
        update_tree_on_donation(socketio, mongo.db, donor_name, amount)

        print(f"Processed payment for {donor_name}: ${amount}")

    return jsonify(success=True), 200