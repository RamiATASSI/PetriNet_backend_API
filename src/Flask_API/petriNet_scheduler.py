from flask_socketio import SocketIO

from src.PetriNet_algo.objects import jsons_to_objects, objects_to_jsons
from src.PetriNet_algo.petriNet import PetriNet


class PetriNetScheduler:
    def __init__(self, json, user_id, socketio):
        self.colors, self.places, self.transitions = self._json_to_objects(json)
        self.user_id = user_id
        self.socketio = socketio
        self.sensitive_transitions = []
        self.triggered_transitions = []
        self.paused = False
        
        # Initial setup
        self._emit_setup()
    
    def _emit_setup(self):
        """Emit initial state to client"""
        try:
            self.socketio.emit('set_up', self._get_state(), room=self.user_id)
        except Exception as e:
            print(f"Error in _emit_setup: {e}")

    def _emit_update(self):
        """Emit state update to client"""
        try:
            self.socketio.emit('update', self._get_state(), room=self.user_id)
        except Exception as e:
            print(f"Error in _emit_update: {e}")

    def _emit_message(self, message):
        """Emit message to client"""
        try:
            self.socketio.emit('message', message, room=self.user_id)
        except Exception as e:
            print(f"Error in _emit_message: {e}")

    def tic(self):
        """Main update cycle"""
        if self.paused:
            return
            
        # Update sensitization states
        self.sensitive_transitions = []
        for transition in self.transitions.values():
            if transition.check_sensitization():
                self.sensitive_transitions.append(transition)
        
        # Emit current state
        self._emit_update()

    def shortcut_trigger_transition(self, transition_name):
        """Handle manual transition triggering"""
        if transition_name not in self.transitions:
            self._emit_message(f"Transition {transition_name} not found")
            return

        transition = self.transitions[transition_name]
        
        # Check sensitization
        if not transition.check_sensitization():
            self._emit_message(f"Can't trigger non-sensitized transition {transition_name}")
            return
            
        # Execute the transition
        self._emit_message(f"Triggering transition {transition_name}")
        
        # Consume tokens
        deleted_colors = transition.consume_tokens()
        self._emit_message(f"Consumed tokens from: {[str(place) for place in deleted_colors.keys()]}")
        
        # Produce tokens
        added_colors = transition.produce_tokens()
        self._emit_message(f"Produced tokens to: {[str(place) for place in added_colors.keys()]}")
        
        # Update state
        self._emit_update()

    def pause(self):
        """Pause the simulation"""
        self.paused = True
        self._emit_message("Simulation paused")

    def resume(self):
        """Resume the simulation"""
        self.paused = False
        self._emit_message("Simulation resumed")

    def _get_state(self):
        """Get current state as JSON"""
        places_json, transitions_json = objects_to_jsons(self.places, self.transitions)
        return {
            'places': places_json,
            'transitions': transitions_json
        }

    def _json_to_objects(self, json):
        """Convert JSON to internal objects"""
        return jsons_to_objects(json['colors'], json['places'], json['transitions'])