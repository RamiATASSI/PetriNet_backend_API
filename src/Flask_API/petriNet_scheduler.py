from flask_socketio import SocketIO

from src.PetriNet_algo.objects import jsons_to_objects, objects_to_jsons
from src.PetriNet_algo.petriNet import PetriNet


class PetriNetScheduler(PetriNet):
    def __init__(self, json, user_id, socketio: SocketIO):
        super().__init__(*self._json_to_objects(json))
        self.user_id = user_id
        self.socketio = socketio
        self.socketio.emit('set_up', self._get_state(), room=self.user_id)


    def tic(self):
        super().tic()
        self.socketio.emit('update', self._get_state(), room=self.user_id)


    def shortcut_trigger_transition(self, transition_name):
        transition = self.transitions[transition_name]
        
        # 1) Check if it’s sensitized
        transition.check_sensitization()
        if not transition.is_sensitized:
            self.socketio.emit('message', f"Can't trigger not sensitized transition {transition_name}", room=self.user_id)
            return

        # 2) Trigger if sensitized (sets `is_triggered = True`)
        transition.shortcut_trigger_if_sensitized()

        # 3) Actually consume and produce tokens
        transition.consume_tokens()
        transition.produce_tokens()

        # 4) Emit feedback and updated state
        self.socketio.emit('message', f"Transition '{transition_name}' triggered", room=self.user_id)
        self.socketio.emit('update', self._get_state(), room=self.user_id)

    def _get_state(self):
        return self._objects_to_json(self.places, self.transitions)

    def _objects_to_json(self, places, transitions):
        places_json, transitions_json = objects_to_jsons(places, transitions)
        return {'places': places_json, 'transitions': transitions_json}

    def _json_to_objects(self, json):
        return jsons_to_objects(json['colors'], json['places'], json['transitions'])

    def _json_to_dicts(self, json):
        pass

    def _dicts_to_objects(self, dicts):
        pass
