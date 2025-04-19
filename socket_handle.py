from flask_socketio import SocketIO,emit

socketio = SocketIO(cors_allowed_origins='*', async_mode='eventlet')

def init_s(app):
    
    socketio.init_app(app)
    # To check if frontend is connected or not 
    @socketio.on('connect')
    def connect():
        print("The client has been connected succesfully")
        
    @socketio.on('disconnect')
    def disconnet():
        print("Client has been disconnected")
        
    # testing the connection with a simple ping pong test 
    
    
    @socketio.on('ping_test')
    def ping_handle(data):
        print("Ping has been received from the client\n",data)
        emit('pong_test', {'response': 'Pong from server!'}, broadcast=False) 
        
    # testing the donation part 
    
    @socketio.on('donation_test')
    def test_donation(data):
        print("Test donation has been receieved from the client\n",data)
        emit('donation_received', data, broadcast=True)
        
    
    