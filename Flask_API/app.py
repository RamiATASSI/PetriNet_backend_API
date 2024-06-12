from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from petriNet_scheduler import PetriNetScheduler

app = Flask(__name__)
socketio = SocketIO(app)


active_PetriNets = {}  # Dictionary to store active algorithms keyed by user ID

@app.route('/Petri_run', methods=['POST'])
def run_algorithm():
    if request.method == 'POST':
        data_json = request.json
        user_id = request.sid  # Use socket ID as user ID
        # Initialize algorithm with data from frontend
        petriNet = PetriNetScheduler(json= data_json, emit_func= lambda event, data: emit(event, data, room=user_id))
        # Start algorithm in a separate thread
        petriNet.run_thread(tic_time=1)
        active_PetriNets[user_id] = petriNet  # Store algorithm instance for the user
        return jsonify({'message': 'Algorithm started successfully'}), 200
    else:
        return jsonify({'error': 'Only POST requests are allowed'}), 405

@socketio.on('disconnect')
def disconnect():
    user_id = request.sid
    if user_id in active_PetriNets:
        del active_PetriNets[user_id]

if __name__ == '__main__':
    socketio.run(app, debug=True)  # Run the Flask app with SocketIO
