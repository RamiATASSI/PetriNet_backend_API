from flask import request
import traceback
from flask_socketio import emit
from .extensions import socketio, scheduler
from .petriNet_scheduler import PetriNetScheduler

# Store active PetriNets
active_PetriNets = {}

@socketio.on('connect')
def connect():
    user_id = request.sid
    print(f"User {user_id} connected")
    emit('message', f'Connected to the server: {user_id}', room=user_id)

@socketio.on('disconnect')
def disconnect():
    user_id = request.sid
    if user_id in active_PetriNets:
        job_id = f'feedback_job_{user_id}'
        try:
            scheduler.remove_job(job_id)
        except:
            pass
        del active_PetriNets[user_id]
    print(f"User {user_id} disconnected")

@socketio.on('run')
def handle_run(json):
    user_id = request.sid
    
    # Check if already running
    if user_id in active_PetriNets:
        emit('error', 'PetriNet is already running for this user', room=user_id)
        return
        
    try:
        # Create new PetriNet instance
        petri_net = PetriNetScheduler(json=json, user_id=user_id, socketio=socketio)
        
        # Add to scheduler
        job_id = f'feedback_job_{user_id}'
        scheduler.add_job(
            id=job_id,
            func=petri_net.tic,
            trigger='interval',
            seconds=1
        )
        
        # Store instance
        active_PetriNets[user_id] = petri_net
        
        emit('message', 'Algorithm started successfully', room=user_id)
        
    except Exception as e:
        error_message = f'Error starting PetriNet: {str(e)}'
        traceback_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        print(error_message, traceback_str)
        emit('error', {'error': error_message, 'traceback': traceback_str}, room=user_id)

@socketio.on('transition_trigger')
def handle_transition_trigger(transition_id):
    user_id = request.sid
    
    if user_id not in active_PetriNets:
        emit('error', 'No running PetriNet for this user', room=user_id)
        return
        
    petri_net = active_PetriNets[user_id]
    petri_net.shortcut_trigger_transition(transition_id)

@socketio.on('pause')
def handle_pause():
    user_id = request.sid
    if user_id in active_PetriNets:
        active_PetriNets[user_id].pause()
        job_id = f'feedback_job_{user_id}'
        scheduler.pause_job(job_id)

@socketio.on('resume')
def handle_resume():
    user_id = request.sid
    if user_id in active_PetriNets:
        active_PetriNets[user_id].resume()
        job_id = f'feedback_job_{user_id}'
        scheduler.resume_job(job_id)

@socketio.on('end')
def handle_end():
    user_id = request.sid
    if user_id in active_PetriNets:
        job_id = f'feedback_job_{user_id}'
        try:
            scheduler.remove_job(job_id)
        except:
            pass
        del active_PetriNets[user_id]
        emit('message', 'PetriNet ended successfully', room=user_id)