from flask_socketio import SocketIO
from datetime import datetime, timezone 

tree_id = "main_tree" 

def get_next_available_branch(mongo):
    # Fetch the tree state from MongoDB
    tree_col = mongo.db.tree_state
    tree_doc = tree_col.find_one({'_id': tree_id}) 
    
    if not tree_doc or 'branches' not in tree_doc:
        # Initialize branches if not present (assume 5 branches for simplicity)
        tree_doc = {
            '_id': tree_id,
            'total_donations': 0,
            'stage': 1,
            'branches': ['branch_1', 'branch_2', 'branch_3', 'branch_4', 'branch_5']  # 5 branches
        }
        tree_col.insert_one(tree_doc)

    for branch_index, branch in enumerate(tree_doc['branches']):
        if branch == "empty":
            return branch_index
    
    return len(tree_doc['branches']) % len(tree_doc['branches'])  # This is just a fallback 


def emit_donor_label(socketio, mongo, donor_name, amount):
    # Get the next available branch
    branch_index = get_next_available_branch(mongo)

    # Emit the event with donor info and branch index
    socketio.emit('new_donor_label', {
        'name': donor_name,
        'amount': amount,
        'branchIndex': branch_index
    })
    
    tree_col = mongo.db.tree_state
    tree_doc = tree_col.find_one({'_id': tree_id})
    tree_doc['branches'][branch_index] = f"donor_{donor_name}"  # Mark the branch as taken by the donor
    tree_col.update_one({'_id': tree_id}, {'$set': {'branches': tree_doc['branches']}}) 
    
    
    
def update_tree_on_donation(socketio, mongo, donor_name, amount):
    # Insert donor data into MongoDB (similar to the logic you've already done)
    donor_data = {
        "name": donor_name,
        "amount": amount,
        "timestamp": datetime.now(tz=timezone.utc)
    }
    mongo.db.donor_data.insert_one(donor_data)


    emit_donor_label(socketio, mongo, donor_name, amount)
    