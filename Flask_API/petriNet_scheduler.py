from apscheduler.schedulers.background import BackgroundScheduler

from PetriNet_algo.petriNet import PetriNet
from PetriNet_algo.objects import jsons_to_objects, objects_to_jsons


class PetriNetScheduler(PetriNet):
    def __init__(self, json, emit_func):
        super().__init__(*self._json_to_objects(json))
        self.scheduler = BackgroundScheduler()
        self.emit_func = emit_func

    def run_thread(self, tic_time=1):
        self.scheduler.add_job(self.tic, 'interval', seconds=tic_time)
        self.scheduler.start()

    def pause(self):
        self.scheduler.pause()

    def resume(self):
        self.scheduler.resume()

    def stop(self):
        self.scheduler.shutdown()

    def tic(self):
        super().tic()
        self.emit_func('update', self._get_state())

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
