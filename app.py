from flask import Flask, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
socketio = SocketIO(app)


device_list = []

@app.route('/')
def index():
	return jsonify(devices=device_list)


@socketio.on('login')
def on_login(app_id):
	print("%s logged in." % app_id)
	emit("login", {'devices': device_list})


@socketio.on('logout')
def on_logout(app_id):
	print("%s logged out." % app_id)


@socketio.on('subscribe')
def on_subscribe(device_id):
	join_room(device_id)


@socketio.on('unsubscribe')
def on_unsubscribe(device_id):
	leave_room(device_id)


@socketio.on('register')
def on_register(device_id):
	device_list.append(device_id)
	print(device_list)


@socketio.on('deregister')
def on_deregister(device_id):
	device_list.remove(device_id)
	print(device_list)


@socketio.on('emg')
def on_emg(data):
	device_id = data.get('device_id')
	emg_data = data.get('emg')
	print("receive %s from device %s" % (emg_data, device_id))
	emit("emg", emg_data, room = device_id)


@socketio.on('message')
def handle_message(message):
    print('received message: %s' % message)

    
if __name__ == '__main__':
    socketio.run(app)