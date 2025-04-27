# test_donation.py
from flask_socketio import SocketIO
from tree_logic import update_tree_on_donation

def setup_donation_handlers(socketio):
    @socketio.on('test_donation')
    def handle_test_donation(data):
        # Extract data from the event
        donor_name = data.get('name', 'Anonymous')
        amount = data.get('amount', 0)
        
        # Get mongo from app context
        with socketio.app.app_context():
            mongo = socketio.app.extensions['pymongo']
            
            # Use the same logic as the real donation handler
            update_tree_on_donation(socketio, mongo.db, donor_name, amount)