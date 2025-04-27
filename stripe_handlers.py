import stripe
import os
from flask import request, jsonify, session

def setup_stripe_handlers(app):
    @app.route('/create-checkout-session', methods=['POST'])
    def create_checkout_session():
        try:
            data = request.json
            donor_name = data.get('name', 'Anonymous')
            amount = data.get('amount', 5)
            
            # Store donor name in session for retrieval after payment
            session['donor_name'] = donor_name
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Donation to Giving Tree Gala',
                            'description': f'Donation from {donor_name}',
                        },
                        'unit_amount': int(amount * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.host_url + 'donation-success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.host_url + 'watch',
                metadata={
                    'donor_name': donor_name,
                }
            )
            
            return jsonify({'id': checkout_session.id})
        except Exception as e:
            return jsonify(error=str(e)), 400
            
    @app.route('/donation-success')
    def donation_success():
        session_id = request.args.get('session_id')
        if not session_id:
            return "Session ID not found", 400
            
        try:
            # Verify the session was successful
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            return f"""
            <html>
            <head>
                <title>Donation Successful</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 40px; }}
                    .success {{ color: #2d5a27; margin-bottom: 20px; }}
                    .button {{ background-color: #2d5a27; color: white; padding: 10px 20px; 
                        text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <h1 class="success">Thank You for Your Donation!</h1>
                <p>Your contribution will make a difference.</p>
                <p>Your donation of ${checkout_session.amount_total/100:.2f} has been processed successfully.</p>
                <a class="button" href="/watch">Return to Live Stream</a>
            </body>
            </html>
            """
        except Exception as e:
            return str(e), 400