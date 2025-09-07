from typing import Dict, List

from src.PetriNet_algo.object.place import Place, PlaceId
from src.PetriNet_algo.object.transition import Transition


class PetriNet:
    """
    A Petri net with:
    type_forest: the TypeForest of all token types
    places:       map of PlaceId to Place
    transitions:  map of transition name to Transition
    """

    def __init__(
        self,
        type_forest,
        places: Dict[PlaceId, Place],
        transitions: Dict[str, Transition]
    ):
        self.type_forest = type_forest
        self.places = places
        self.place_dict = places
        self.transitions = transitions

        
        self.sensitive_transitions: List[Transition] = []
        self.triggered_transitions: List[Transition] = []

        #first sensitization pass
        self._update_sensitized()

    def _update_sensitized(self):
        self.sensitive_transitions = [
            t for t in self.transitions.values()
            if t.check_sensitization()
        ]

    def tic(self):
        """
        One firing step:
        Recompute sensitized transitions. For each sensitized transition:
        1.consume tokens via ConditionSwitch
        2. apply its OperatorGraph to produce new tokens
        3. make sure tokens are in the correct places as outputs their output places
        """
        self._update_sensitized()
        fired = []
        for t in self.sensitive_transitions:
            consumed = t.consume_tokens(self.place_dict)
            if consumed is None:
                continue
            produced = t.produce_tokens()
            for pl_name, toks in produced.items():
                self.place_dict[pl_name].add_tokens(toks)
            fired.append(t)
        self.triggered_transitions = fired
        # after firing, recompute sensitization
        self._update_sensitized()

    def print_details(self):
        print("Places")
        for name, place in self.places.items():
            toks = place.get_tokens()
            print(f"  {name}: {[str(t) for t in toks]}")
        print("Sensitive Transitions")
        print([t.transition_name for t in self.sensitive_transitions])
        print("Last Fired")
        print([t.transition_name for t in self.triggered_transitions])


def main():
    """
    Demo of marry and adopt cat:
    """

    types_json = {
        "LivingBeing": {"parent": None},
        "Human":       {"parent": "LivingBeing"},
        "Animal":      {"parent": "LivingBeing"},
        "Man":         {"parent": "Human"},
        "Woman":       {"parent": "Human"},
        "Cat":         {"parent": "Animal"},
        "Family":      {"parent": None},
    }


    places_json = {
        "Start": {
            "initial_tokens": [
                {"type": "Man",   "attributes": {"lastName": "Smith"}},
                {"type": "Woman", "attributes": {"lastName": "Clark"}},
                {"type": "Cat",   "attributes": {"name": "Nala"}}
            ]
        },
        "End": {"initial_tokens": []}
    }


    transitions_json = {
        "marry_and_adopt": {
            "condition_switch": {
                "hasPriorityOrder": True,
                "conditionLists": [
                    {
                        "conditions": [
                            {
                                "id": "c_man",
                                "consumption": {"Start": ["Man"]},
                                "predicate": "true",
                                "outputs": ["op_gen_family", "op_set_married_man", "op_merge_man"]
                            },
                            {
                                "id": "c_woman",
                                "consumption": {"Start": ["Woman"]},
                                "predicate": "true",
                                "outputs": ["op_copy_last_name_to_woman", "op_set_married_woman", "op_merge_woman"]
                            },
                            {
                                "id": "c_cat",
                                "consumption": {"Start": ["Cat"]},
                                "predicate": "true",
                                "outputs": ["op_copy_last_name_to_cat", "op_merge_cat"]
                            }
                        ]
                    }
                ]
            },
            "operator_graph": {
                "operators": [
                    # Create a Family token based on an incoming token
                    {
                        "id": "op_gen_family",
                        "dest": "End",
                        "transform": "generate_family",
                        "inputChannels":  {"normal": True},
                        "outputChannels": {"normal": True}
                    },
                    # Attribute updates on the humans
                    {
                        "id": "op_set_married_man",
                        "dest": "End",
                        "transform": "set_married",
                        "inputChannels":  {"normal": True},
                        "outputChannels": {"normal": True}
                    },
                    {
                        "id": "op_set_married_woman",
                        "dest": "End",
                        "transform": "set_married",
                        "inputChannels":  {"normal": True},
                        "outputChannels": {"normal": True}
                    },
                    # Copy family last name to Woman / Cat before merging them into Family
                    {
                        "id": "op_copy_last_name_to_woman",
                        "dest": "End",
                        "transform": "copy_last_name",
                        "inputChannels":  {"normal": True},
                        "outputChannels": {"normal": True}
                    },
                    {
                        "id": "op_copy_last_name_to_cat",
                        "dest": "End",
                        "transform": "copy_last_name",
                        "inputChannels":  {"normal": True},
                        "outputChannels": {"normal": True}
                    },
                    # Merge each into the Family token
                    {
                        "id": "op_merge_cat",
                        "dest": "End",
                        "transform": "merge_into_family",
                        "inputChannels":  {"normal": True},
                        "outputChannels": {"normal": True}
                    },
                    {
                        "id": "op_merge_man",
                        "dest": "End",
                        "transform": "merge_into_family",
                        "inputChannels":  {"normal": True},
                        "outputChannels": {"normal": True}
                    },
                    {
                        "id": "op_merge_woman",
                        "dest": "End",
                        "transform": "merge_into_family",
                        "inputChannels":  {"normal": True},
                        "outputChannels": {"normal": True}
                    }
                ],
                "edges": [
                    # Family should be available to merges
                    {"from": "op_gen_family",            "to": "op_merge_man"},
                    {"from": "op_gen_family",            "to": "op_merge_woman"},
                    {"from": "op_gen_family",            "to": "op_merge_cat"},

                    # Name gets copied before merging
                    {"from": "op_copy_last_name_to_woman","to": "op_merge_woman"},
                    {"from": "op_copy_last_name_to_cat",  "to": "op_merge_cat"}
                ]
            }
        }
    }

    # transfor registry
    registry_ctx = {
        "family_name": None,
        "family_token": None,   
        "types_json":  types_json,  #for debugging purposes
    }

    FamilyT = None
    HumanT  = None

    def _ensure_family_seed():
        """Create (or return existing) Family SuperToken accumulator."""
        if registry_ctx["family_token"] is None:
            lname = registry_ctx["family_name"] or "Family"
            registry_ctx["family_token"] = SuperToken(FamilyT, {"lastName": lname}, [])
        return registry_ctx["family_token"]

    # transformations
    def generate_family(tok):
        if registry_ctx["family_name"] is None:
            registry_ctx["family_name"] = tok.attributes.get("lastName") or "Family"
        fam = _ensure_family_seed()
        return fam

    def set_married(tok):
        tok.attributes["maritalStatus"] = "married"
        return tok

    def copy_last_name(tok):
        lname = registry_ctx["family_name"] or tok.attributes.get("lastName") or "Family"
        tok.attributes["lastName"] = lname
        return tok

    def merge_into_family(tok):
        fam = _ensure_family_seed()
        if tok.type.name in ("Man", "Woman"):
            child = SimpleToken(HumanT, dict(tok.attributes))
        else:
            child = tok
        # to avoid duplicates if called multiple times
        if child not in fam.children:
            fam.children.append(child)
        return fam

    # Build a registry of transformations
    TRANSFORMS = {
        "generate_family":    generate_family,
        "set_married":        set_married,
        "copy_last_name":     copy_last_name,
        "merge_into_family":  merge_into_family,
    }

    # Attach them to OperatorGraph so objects.py can resolve by getattr()
    for name, fn in TRANSFORMS.items():
        setattr(OperatorGraph, name, fn)

    # building the petri net
    type_forest, places, transitions = jsons_to_objects(
        types_json, places_json, transitions_json
    )
    FamilyT = type_forest.get_type("Family")
    HumanT  = type_forest.get_type("Human")

    net = PetriNet(type_forest, places, transitions)

    # running demo
    net.print_details("Before firing")
    net.tic()
    net.print_details("After one tick")

    # should no longer be sensitized, since inputs are consumed
    t = transitions["marry_and_adopt"]
    print(f"\n'marry_and_adopt' sensitized after tick? {bool(t.check_sensitization())}")

if __name__ == "__main__":
    main()
