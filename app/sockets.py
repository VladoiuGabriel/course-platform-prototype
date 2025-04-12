from flask_socketio import SocketIO, send
from app import socketio

@socketio.on("message")
def handle_message(msg):
    print(f"Mesaj primit: {msg}")
    send(msg, broadcast=True)
@socketio.on('join_room')
def handle_join_room_event(data):
    room = data['room']
    username = data['username']
    socketio.emit('user_joined', {'username': username}, room=room)
    socketio.join_room(room)

@socketio.on('offer')
def handle_offer(data):
    socketio.emit('offer', data, room=data['room'])

@socketio.on('answer')
def handle_answer(data):
    socketio.emit('answer', data, room=data['room'])

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    socketio.emit('ice_candidate', data, room=data['room'])