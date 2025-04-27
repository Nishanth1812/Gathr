from datetime import datetime, timezone
from flask_socketio import SocketIO

tree_id = "main_tree"

def init_tree_state(mongo):
    db = mongo.db
    tree_col = db['tree_state']
    if not tree_col.find_one({'_id': tree_id}):
        tree_col.insert_one({
            '_id': tree_id,
            'total_donations': 0,
            'stage': 1,
            'branches': ['empty'] * 5  # Initialize 5 empty branches
        })

def get_tree_state(mongo):
    tree_col = mongo['tree_state']
    tree_doc = tree_col.find_one({'_id': tree_id})
    if not tree_doc:
        init_tree_state({'db': mongo})
        tree_doc = tree_col.find_one({'_id': tree_id})
    
    # Get recent donors
    recent_donors = list(mongo['donor_data'].find().sort('timestamp', -1).limit(5))
    
    # Convert ObjectId to string and format timestamps
    for donor in recent_donors:
        if '_id' in donor:
            donor['_id'] = str(donor['_id'])
        if 'timestamp' in donor:
            donor['timestamp'] = donor['timestamp'].isoformat()
    
    return {
        'total_donations': tree_doc.get('total_donations', 0),
        'stage': tree_doc.get('stage', 1),
        'branches': tree_doc.get('branches', ['empty'] * 5),
        'recent_donors': recent_donors
    }

def get_next_available_branch(mongo):
    tree_col = mongo['tree_state']
    tree_doc = tree_col.find_one({'_id': tree_id})
    
    # Find first empty branch
    for index, status in enumerate(tree_doc['branches']):
        if status == 'empty':
            return index
    
    # If all branches are full, use round-robin approach
    return (tree_doc.get('last_used_branch', -1) + 1) % len(tree_doc['branches'])

def emit_donor_label(socketio, mongo, donor_name, amount):
    branch_index = get_next_available_branch(mongo)
    
    # Atomic update of branch status
    tree_col = mongo['tree_state']
    tree_col.update_one(
        {'_id': tree_id},
        {
            '$set': {
                f'branches.{branch_index}': 'occupied', 
                'last_used_branch': branch_index
            },
            '$inc': {'total_donations': amount}
        }
    )
    
    # Insert donor data
    donor_data = {
        "name": donor_name,
        "amount": amount,
        "branch_index": branch_index,
        "timestamp": datetime.now(timezone.utc)
    }
    mongo['donor_data'].insert_one(donor_data)
    
    # Emit to all clients
    socketio.emit('new_donor_label', {
        'name': donor_name,
        'amount': amount,
        'branchIndex': branch_index
    })
    
    return True

def update_tree_on_donation(socketio, mongo, donor_name, amount):
    success = emit_donor_label(socketio, mongo, donor_name, amount)
    if not success:
        # Retry once if concurrent update failed
        emit_donor_label(socketio, mongo, donor_name, amount)