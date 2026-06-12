from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'padhai_secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

users_in_room = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = data['username']
    join_room(room)

    # FIX: Yaha [room] lagana tha. Ye list hai, dict nahi
    if room not in users_in_room:
        users_in_room[room] = [] # <-- Yahi line galat thi
    users_in_room[room].append(request.sid)

    print(f"{username} joined room {room}")

    # Agar room me 1 se zyada log hain to purane wale ko batao
    if len(users_in_room[room]) > 1:
        emit('other_user', {'username': username}, room=room, include_self=False)
    else:
        emit('user_joined', {'sid': request.sid, 'username': username}, room=room)

@socketio.on('offer')
def handle_offer(data):
    emit('offer', data, room=data['room'], include_self=False)

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, room=data['room'], include_self=False)

@socketio.on('candidate')
def handle_candidate(data):
    emit('candidate', data, room=data['room'], include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    for room, users in list(users_in_room.items()):
        if request.sid in users:
            users.remove(request.sid)
            emit('user_left', {'sid': request.sid}, room=room)
            print(f"User left room {room}")
            if not users:
                del users_in_room[room]

if __name__ == '__main__':
    print("Server running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)