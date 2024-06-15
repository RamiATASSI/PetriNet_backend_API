from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_apscheduler import APScheduler
from petriNet_scheduler import PetriNetScheduler

app = Flask(__name__)
socketio = SocketIO(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

active_PetriNets = {}  # Dictionary to store active algorithms keyed by user ID


@app.route('/')
def test():
    return render_template('index.html')


@socketio.on('connect')
def connect():
    user_id = request.sid
    print(f"User {user_id} connected")


@socketio.on('disconnect')
def disconnect():
    user_id = request.sid
    if user_id in active_PetriNets:
        job_id = f'feedback_job_{user_id}'
        scheduler.remove_job(job_id)
        del active_PetriNets[user_id]
    print(f"User {user_id} disconnected")


@socketio.on('run')
def handle_run(json):
    user_id = request.sid
    if has_active_petriNet(user_id):
        emit('error', 'PetriNet is already running for this user', room=user_id)
        return
    petriNet = PetriNetScheduler(json=json, user_id=user_id, socketio=socketio)
    # Start algorithm in a separate thread
    job_id = f'feedback_job_{user_id}'
    scheduler.add_job(id=job_id, func=petriNet.tic, trigger='interval', seconds=5)
    active_PetriNets[user_id] = petriNet  # Store algorithm instance for the user
    emit('message', 'Algorithm started successfully', room=user_id)


@socketio.on('pause')
def handle_pause():
    user_id = request.sid
    if no_active_petriNet(user_id):
        return
    job_id = f'feedback_job_{user_id}'
    scheduler.pause_job(job_id)
    emit('message', 'PetriNet paused successfully', room=user_id)


@socketio.on('resume')
def handle_resume():
    user_id = request.sid
    if no_active_petriNet(user_id):
        return
    job_id = f'feedback_job_{user_id}'
    scheduler.resume_job(job_id)
    emit('message', 'PetriNet resumed successfully', room=user_id)


def no_active_petriNet(user_id):
    if not has_active_petriNet(user_id):
        emit('error', 'No running PetriNet for this user', room=user_id)
        return True
    return False


def has_active_petriNet(user_id):
    return user_id in active_PetriNets


if __name__ == '__main__':
    socketio.run(app, debug=True)  # Run the Flask app with SocketIO
