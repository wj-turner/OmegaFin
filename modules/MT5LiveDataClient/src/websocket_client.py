import socketio

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print("I'm connected!")
    # sio.emit('my event', {'data': 'Client is connected!'})  # Example event

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.event
def my_response(data):
    print('Received response: ', data)

@sio.event
def mt5_account_info(data):
    print('Received MT5 account info: ', data)

if __name__ == '__main__':
    try:
        sio.connect('http://172.16.14.144:5000')  # Update with your Flask-SocketIO app's address
        sio.wait()
    except socketio.exceptions.ConnectionError as e:
        print("Connection failed:", e)
