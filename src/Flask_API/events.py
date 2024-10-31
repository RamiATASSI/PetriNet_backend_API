from flask import request
import traceback
from flask_socketio import emit
from .extensions import socketio, scheduler
from .petriNet_scheduler import PetriNetScheduler

active_PetriNets = {}  # Dictionary to store active algorithms keyed by user ID

@socketio.on('connect')
def connect():
    user_id = request.sid
    print(f"User {user_id} connected")
    emit('message', f'Connected to the server : {user_id}', room=user_id)


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
    try:
        petriNet = PetriNetScheduler(json=json, user_id=user_id, socketio=socketio)
        # Start algorithm in a separate thread
        job_id = f'feedback_job_{user_id}'
        scheduler.add_job(id=job_id, func=petriNet.tic, trigger='interval', seconds=1)
        active_PetriNets[user_id] = petriNet  # Store algorithm instance for the user
        emit('message', 'Algorithm started successfully', room=user_id)
    except Exception as e:
        # Catch any exceptions and notify the client of the error
        error_message = f'Error starting PetriNet: {str(e)}'
        traceback_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        print(error_message, traceback_str)  # Log the error on the server
        emit('error', {'error': error_message, 'traceback': traceback_str}, room=user_id)



@socketio.on('transition_trigger')
def handle_transition_trigger(transition_ID):
    user_id = request.sid
    emit('message', f'Transition triggered : {user_id}', room=user_id)
    if no_active_petriNet(user_id):
        return
    petriNet = active_PetriNets[user_id]
    petriNet.shortcut_trigger_transition(transition_ID)



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


@socketio.on('end')
def handle_end():
    user_id = request.sid
    if no_active_petriNet(user_id):
        return
    job_id = f'feedback_job_{user_id}'
    scheduler.remove_job(job_id)
    del active_PetriNets[user_id]
    emit('message', 'PetriNet ended successfully', room=user_id)



def no_active_petriNet(user_id):
    if not has_active_petriNet(user_id):
        emit('error', 'No running PetriNet for this user', room=user_id)
        return True
    return False


def has_active_petriNet(user_id):
    return user_id in active_PetriNets
