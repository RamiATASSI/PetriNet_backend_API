from flask_socketio import SocketIO

from src.PetriNet_algo.objects import jsons_to_objects, objects_to_jsons
from src.PetriNet_algo.petriNet import PetriNet



class PetriNetScheduler(PetriNet):
    def __init__(self, json, user_id, socketio: SocketIO):
        super().__init__(*self._json_to_objects(json))
        self.user_id = user_id
        self.socketio = socketio

    def tic(self):
        super().tic()
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
