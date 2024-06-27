# from catalogue_design import *
import time

import numpy as np

verbose_level = 0


class PetriNet:

    def __init__(self, colors, places, transitions):
        self.colors = colors
        self.places = places
        self.transitions = transitions

        self.sensitive_transitions = []
        self.triggered_transitions = []
        self.added_colors = {}
        for place in self.places.values():
            self.added_colors[place] = place.get_colors()

    def print_details(self):
        if verbose_level == 2:
            for places in self.places.values():
                places.describe()
            for transitions in self.transitions.values():
                transitions.describe()

    # activate the actions of the places that have been activated
    def activate(self):
        if verbose_level:
            print("Phase 0")
            print("activating")
            self.print_details()

        for place, colors in self.added_colors.items():
            for color in colors:
                if verbose_level:
                    print("Activating place: ", place)
                    print("Color: ", color)
                place.launch_action(color)

    # populates the list of sensitive transitions
    def sensitize(self):
        if verbose_level:
            print("Phase 1")
            print("sensitizing")
            self.print_details()
        self.sensitive_transitions = []
        for transition in self.transitions.values():
            if transition.check_sensitization():
                self.sensitive_transitions.append(transition)

    # check if some of the sensitive transitions are triggered and add them to the list if they are
    def trigger(self):
        if verbose_level:
            print("Phase 2")
            print("triggering")
            self.print_details()
        self.triggered_transitions = []
        self.retrigger()
        if verbose_level:
            print("after triggering")
            self.print_details()

    def retrigger(self):
        # randomize sensitive transitions
        np.random.shuffle(self.sensitive_transitions)

        for transition in self.sensitive_transitions:
            if transition.check_triggered():
                if verbose_level:
                    print("Transition " + str(transition) + " with condition " +
                          transition.triggering_event + " triggered")

                self.triggered_transitions.append(transition)
                self.sensitive_transitions.remove(transition)

                if verbose_level > 1:
                    print("Before consumption: ")
                    self.print_details()
                transition.consume_tokens()
                if verbose_level > 1:
                    print("After consumption: ")
                    self.print_details()
                    print("sensitive_transitions: ", self.sensitive_transitions)
                self.sensitive_transitions = [transition for transition in self.sensitive_transitions if
                                              transition.check_sensitization()]

                if verbose_level:
                    print("new sensitive_transitions after resesitizing: ",
                          [str(transition) for transition in self.sensitive_transitions])
                    self.retrigger()
                break

    def produce(self):
        if verbose_level:
            print("Phase 2")
            print("producing")
            self.print_details()
        self.added_colors = {}
        for transition in self.triggered_transitions:
            transition_added_colors = transition.produce_tokens()

            for place, colors in transition_added_colors.items():
                if place not in self.added_colors:
                    self.added_colors[place] = set()
                self.added_colors[place].update(colors)

        if verbose_level:
            print("After production: ")
            self.print_details()

    def tic(self):
        self.activate()
        self.sensitize()
        self.trigger()
        self.produce()


def main() -> None:
    transitions_json = {
        'Transition1':
            {
                'Token_Consumption':
                    {
                        'Place1':
                            {
                                'Color1': 1,
                                'Color2': 1
                            },
                        'Place2':
                            {
                                'Color2': 1
                            }
                    },
                'Triggering_Event': 'True',
                'Token_Production':
                    {
                        'Place2':
                            {
                                'Color1': 2,
                                'Color2': 1
                            },
                    }
            },
        'Transition2':
            {
                'Token_Consumption':
                    {
                        'Place1':
                            {
                                'Color1': 1,
                                'Color2': 1
                            },
                    },
                'Triggering_Event': 'True',
                'Token_Production':
                    {
                        'Place2':
                            {
                                'Color1': 1,
                                'Color2': 1
                            },
                    }
            }
    }

    places_json = {
        'Place1':
            {
                'Color1':
                    {
                        'Tokens_nbr': 2,
                        'Action': "function11"
                    },
                'Color2':
                    {
                        'Tokens_nbr': 2,
                        'Action': "function21"
                    }
            },
        'Place2':
            {
                'Color1':
                    {
                        'Tokens_nbr': 0,
                        'Action': "function12"
                    },
                'Color2':
                    {
                        'Tokens_nbr': 0,
                        'Action': "function22"
                    }
            }
    }

    colors_json = {
        "Color1":
            {
                "class_name": "Humans",
                "attributes": [
                    {"attribute_name": "attribute11", "attribute_value": "1"},
                    {"attribute_name": "attribute12", "attribute_value": "'value1'"}],
                "functions": [
                    {"function_name": "function11", "function_core": "return self.attribute11"},
                    {"function_name": "function12", "function_core": "self.attribute11 = 3; print(self.attribute11)"}]
            },
        "Color2":
            {
                "class_name": "Animals",
                "attributes": [
                    {"attribute_name": "attribute21", "attribute_value": "2"},
                    {"attribute_name": "attribute22", "attribute_value": "'value2'"}],
                "functions": [
                    {"function_name": "function21", "function_core": "return self.attribute21"},
                    {"function_name": "function22", "function_core": "print('prout')"}]
            }
    }

    petri_net = PetriNet(colors_json, places_json, transitions_json)
    petri_net.print_details()
    while True:
        petri_net.tic()
        time.sleep(1)
    # Example usage
    # timer1 = timerD.TimerD()
    # timer2 = timerD.TimerD()
    # temp_sensor1 = temp_sensor.TempSensor()
    # arduino = arduinoControl.ArduinoControl('COM3')


if __name__ == '__main__':
    main()
