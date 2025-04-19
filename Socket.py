from flask_socketio import SocketIO

def init(socketio: SocketIO):
    
    # To check if frontend is connected or not 
    @socketio.on('connect')
    def connet():
        print("The client has been connected succesfully")
        
    @socketio.on('disconnect')
    def disconnet():
        print("Client has been disconnected")
        
        