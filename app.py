import numpy as np
import json

from flask import Flask, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit, send
from classifier import NNClassifier
from collections import Counter, deque

app = Flask(__name__)
socket_io = SocketIO(app)
knn_classifier = NNClassifier()

device_list = [2, 3, 4]
device_history = {}
device_last_pose = {}
app_list = []


@app.route('/')
def index():
    return jsonify(devices=device_list)


@socket_io.on('login')
def on_login(app_id):
    join_room(app_id)
    if app_id not in app_list:
        app_list.append(app_id)
    print("%s logged in." % app_id)
    send("success")
    emit("device_list", {'devices': device_list})


def send_device_list():
    for app_id in app_list:
        emit("device_list", {'devices': device_list}, room=app_id)


@socket_io.on('logout')
def on_logout(app_id):
    leave_room(app_id)
    app_list.remove(app_id)
    print("%s logged out." % app_id)


@socket_io.on('subscribe')
def on_subscribe(device_id):
    print("Subscribe %d" % device_id)
    join_room(device_id)


@socket_io.on('unsubscribe')
def on_unsubscribe(device_id):
    print("Unsubscribe %d" % device_id)
    leave_room(device_id)


@socket_io.on('register')
def on_register(device_id):
    if device_id not in device_list:
        device_list.append(device_id)
    # deque(iterable, max_length)
    device_init(device_id)
    print(device_list)
    send_device_list()


def device_init(device_id):
    device_history[device_id] = deque([3] * 25, 25)
    device_last_pose[device_id] = 3

@socket_io.on('deregister')
def on_deregister(device_id):
    device_list.remove(device_id)
    device_history.pop(device_id, None)
    print(device_list)
    send_device_list()

@socket_io.on('emg')
def on_emg(data):
    device_id = data.get('device_id')
    emg_data = data.get('emg')

    if device_id not in device_list:
        device_list.append(device_id)
        device_init(device_id)

    proba = knn_classifier.classify(emg_data)
    pose = np.argmax(proba)
    # print emg_data, pose

    device_history.get(device_id).append(pose)
    # most_common(k) return k most common elements in list
    # return (elements, count)

    r, n = Counter(device_history.get(device_id)).most_common(1)[0]
    if n > 12 and r != device_last_pose.get(device_id, 3):
        send_alert({'status': int(r) == 2, 'device_id': device_id})
    device_last_pose[device_id] = r
    # print("receive %s from device %s" % (emg_data, device_id))
    emit("emg", {'emg':emg_data, 'proba':proba[2]}, room=device_id)


@socket_io.on('message')
def handle_message(message):
    print('received message: %s' % message)


def send_alert(alert_info):
    print('-----------device: %d alerted--------------' % (alert_info.get('status')))
    print("App list:", app_list)
    for app_id in app_list:
        emit("alert", alert_info, room=app_id)

if __name__ == '__main__':
    socket_io.run(app, use_reloader=True, host='0.0.0.0')
