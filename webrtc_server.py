# webrtc_server.py
import json
from flask import request, jsonify
from flask_socketio import emit, join_room, leave_room

# Global room for all stream viewers
STREAM_ROOM = "stream_viewers"

# Store the current stream offer for late joiners
current_stream_offer = None
broadcaster_id = None

def setup_webrtc_handlers(socketio, app):
    @socketio.on('connect')
    def handle_connect(auth=None):
        print("Client connected:", request.sid)
        from tree_logic import get_tree_state
        with app.app_context():
            tree_state = get_tree_state(app.extensions['pymongo'].db)
            emit('initial_tree_state', tree_state)

    @socketio.on('disconnect')
    def handle_disconnect():
        global broadcaster_id, current_stream_offer
        if request.sid == broadcaster_id:
            print("Broadcaster disconnected")
            broadcaster_id = None
            current_stream_offer = None
            emit('stream_ended', {}, room=STREAM_ROOM)

    @socketio.on('join_stream')
    def handle_join_stream():
        join_room(STREAM_ROOM)
        print(f"Client {request.sid} joined stream room")
        
        global current_stream_offer
        if current_stream_offer:
            emit('stream_offer', current_stream_offer)

    @socketio.on('leave_stream')
    def handle_leave_stream():
        leave_room(STREAM_ROOM)
        print(f"Client {request.sid} left stream room")

    @socketio.on('broadcaster_ready')
    def handle_broadcaster_ready(data):
        global broadcaster_id
        broadcaster_id = request.sid
        print(f"Broadcaster {request.sid} is ready")
        emit('stream_available', {}, room=STREAM_ROOM)

    @socketio.on('stream_offer')
    def handle_stream_offer(data):
        global current_stream_offer
        current_stream_offer = data
        emit('stream_offer', data, room=STREAM_ROOM, include_self=False)

    @socketio.on('viewer_answer')
    def handle_viewer_answer(data):
        global broadcaster_id
        if broadcaster_id:
            emit('viewer_answer', data, room=broadcaster_id)

    @socketio.on('ice_candidate')
    def handle_ice_candidate(data):
        target_id = data.get('target')
        candidate = data.get('candidate')
        
        if target_id:
            emit('ice_candidate', {'candidate': candidate}, room=target_id)
        else:
            global broadcaster_id
            if request.sid == broadcaster_id:
                emit('ice_candidate', {'candidate': candidate}, room=STREAM_ROOM, include_self=False)
            else:
                emit('ice_candidate', {'candidate': candidate}, room=broadcaster_id)
