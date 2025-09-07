from src.PetriNet_algo.object.place import Place
from src.PetriNet_algo.object.transition import Transition
from .deserializer import ColorDeserializer

from src.PetriNet_algo.deserializer import TypeForestDeserializer
from src.PetriNet_algo.object.token import SimpleToken, SuperToken
from src.PetriNet_algo.object.place import Place
from src.PetriNet_algo.object.transition import Transition
from src.PetriNet_algo.object.transition.condition import Condition, ConditionList, ConditionSwitch
from src.PetriNet_algo.object.transition.operator import Operator, OperatorGraph


def _build_condition_switch(
    js: dict,
    type_forest,
    places: dict[str, Place]
) -> ConditionSwitch:
    """
    If js["conditionLists"] is missing or empty, we treat it as a single
    empty ConditionList (i.e. always true).
    """
    raw_lists = js.get("conditionLists")
    built_lists: list[ConditionList] = []

    # one empty AND-clause for an unconditional branch
    if not raw_lists:
        built_lists.append(ConditionList([]))
    else:
        for branch in raw_lists:
            branch_conds: list[Condition] = []
            for cjs in branch.get("conditions", []):
                cond_id = cjs["id"]
                consumption_spec = cjs.get("consumption", {})
                predicate_spec = cjs.get("predicate", "true").lower()
                outputs = cjs.get("outputs", [])

                # resolve place dependencies from consumption keys
                place_deps = [places[pn] for pn in consumption_spec.keys()]

                # consumption_condition
                def make_consumption(cons_map):
                    def consumption_condition(token_map):
                        selected: dict[str, list] = {}
                        for pname, types in cons_map.items():
                            avail = token_map.get(pname, [])
                            picked: list = []
                            for tname in types:
                                for tok in avail:
                                    if tok.type.name == tname:
                                        picked.append(tok)
                                        break
                                else:
                                    return None
                            selected[pname] = picked
                        return selected
                    return consumption_condition

                consumption_condition = make_consumption(consumption_spec)
                fetch_order = lambda token_map: token_map

                # additional_condition
                if predicate_spec == "true":
                    additional_condition = lambda _: True
                elif predicate_spec == "false":
                    additional_condition = lambda _: False
                else:
                    raise ValueError(f"Unsupported predicate: {predicate_spec}")

                branch_conds.append(
                    Condition(
                        condition_id=cond_id,
                        place_dependencies=place_deps,
                        operator_dest=outputs,
                        consumption_condition=consumption_condition,
                        fetch_order=fetch_order,
                        additional_condition=additional_condition
                    )
                )
            built_lists.append(ConditionList(branch_conds))

    return ConditionSwitch(
        built_lists,
        has_priority_order=js.get("hasPriorityOrder", False)
    )


def _build_operator_graph(spec: dict, type_forest) -> OperatorGraph:
    ops = []
    lookup = {}
    for o in spec.get("operators", []):
        tfm_name = o.get("transform", "identity")
        transform = (lambda tok: tok) if tfm_name == "identity" else getattr(OperatorGraph, tfm_name)

        op = Operator(
            id=o["id"],
            dest=o["dest"],
            transform=transform,
            input_channels=o.get("inputChannels", {}),
            output_channels=o.get("outputChannels", {}),
        )
        ops.append(op)
        lookup[op.id] = op

    edges = [
        (lookup[e["from"]], lookup[e["to"]])
        for e in spec.get("edges", [])
    ]
    return OperatorGraph(ops, edges)


def jsons_to_objects(
    types_json: dict,
    places_json: dict,
    transitions_json: dict
):
    """
    Converts JSON specs into live objects:
      - types_json: definitions of token types
      - places_json: places to initial token specs
      - transitions_json: transitions to JSON specs for conditions & operators

    Returns:
      (type_forest, places_dict, transitions_dict)
    """
    # 1. Build the token-type forest
    type_deser = TypeForestDeserializer()
    type_forest = type_deser.compile(types_json)

    # 2. Recursive builder for SimpleToken vs SuperToken
    def build_token(spec: dict):
        ttype = type_forest.get_type(spec["type"])
        attrs = spec.get("attributes", {})
        children = spec.get("children", [])
        if children:
            return SuperToken(ttype, attrs, [build_token(ch) for ch in children])
        return SimpleToken(ttype, attrs)

    # 3. Instantiate Place objects
    places: dict[str, Place] = {}
    for pname, pspec in places_json.items():
        initial = [build_token(tok) for tok in pspec.get("initial_tokens", [])]
        places[pname] = Place(pname, type_forest, initial)

    # 4. Instantiate Transition objects
    transitions: dict[str, Transition] = {}
    for tname, tspec in transitions_json.items():
        cond_js = tspec.get("condition_switch", {})
        op_js   = tspec.get("operator_graph", {})

        cond_switch = _build_condition_switch(cond_js, type_forest, places)
        op_graph    = _build_operator_graph(op_js, type_forest)
        triggering_event = tspec.get("triggering_event", None)

        transitions[tname] = Transition(
            tname,
            cond_switch,
            op_graph,
            triggering_event=triggering_event
        )

    return type_forest, places, transitions


def _get_state(self):
        return self.objects_to_json(self.type_forest, self.places, self.transitions)


def main() -> None:
    """
    Demo: the 'throuple with cat' transition
    (man and woman marry and adopt a cat) from the report.

    Consume one Man, one Woman and one Cat and produce a Family.
    """
    from src.PetriNet_algo.objects import jsons_to_objects

    # Token type hierarchy
    types_json = {
        "LivingBeing": {"parent": None},
        "Human":       {"parent": "LivingBeing"},
        "Animal":      {"parent": "LivingBeing"},
        "Man":         {"parent": "Human"},
        "Woman":       {"parent": "Human"},
        "Cat":         {"parent": "Animal"},
        "Dog":         {"parent": "Animal"},
        "Family":      {"parent": None},
    }

    # two places: Start (with one of each), End empty
    places_json = {
        "Start": {
            "initial_tokens": [
                {"type": "Man",   "attributes": {"lastName": "Smith"}},
                {"type": "Woman", "attributes": {"lastName": "Clark"}},
                {"type": "Cat",   "attributes": {"name": "Nala"}},
                {"type": "Dog",   "attributes": {"name": "Rex"}}
            ]
        },
        "End": {"initial_tokens": []}
    }

    # a single transition: consume Man, Woman, Cat and produce Family
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
                                "outputs": ["op_set_married", "op_merge_man"]
                            },
                            {
                                "id": "c_woman",
                                "consumption": {"Start": ["Woman"]},
                                "predicate": "true",
                                "outputs": ["op_dup_name_woman", "op_merge_woman"]
                            },
                            {
                                "id": "c_cat",
                                "consumption": {"Start": ["Cat"]},
                                "predicate": "true",
                                "outputs": ["op_dup_name_cat", "op_merge_cat"]
                            }
                        ]
                    }
                ]
            },
            "operator_graph": {
                "operators": [
                    {
                        "id": "op_gen_family",
                        "dest": "End",
                        "transform": "identity",
                        "inputChannels":  {"normal": True, "special": False},
                        "outputChannels": {"normal": True, "special": False}
                    },
                    {
                        "id": "op_dup_name_woman",
                        "dest": "End",
                        "transform": "identity",
                        "inputChannels":  {"normal": True, "special": False},
                        "outputChannels": {"normal": True, "special": False}
                    },
                    {
                        "id": "op_dup_name_cat",
                        "dest": "End",
                        "transform": "identity",
                        "inputChannels":  {"normal": True, "special": False},
                        "outputChannels": {"normal": True, "special": False}
                    },
                    {
                        "id": "op_set_married",
                        "dest": "End",
                        "transform": "identity",
                        "inputChannels":  {"normal": True, "special": False},
                        "outputChannels": {"normal": True, "special": False}
                    },
                    {
                        "id": "op_merge_cat",
                        "dest": "End",
                        "transform": "identity",
                        "inputChannels":  {"normal": True, "special": False},
                        "outputChannels": {"normal": True, "special": False}
                    },
                    {
                        "id": "op_merge_man",
                        "dest": "End",
                        "transform": "identity",
                        "inputChannels":  {"normal": True, "special": False},
                        "outputChannels": {"normal": True, "special": False}
                    },
                    {
                        "id": "op_merge_woman",
                        "dest": "End",
                        "transform": "identity",
                        "inputChannels":  {"normal": True, "special": False},
                        "outputChannels": {"normal": True, "special": False}
                    }
                ],
                "edges": [
                    {"from": "op_gen_family",     "to": "op_merge_cat"},
                    {"from": "op_dup_name_woman", "to": "op_set_married"},
                    {"from": "op_dup_name_cat",   "to": "op_merge_cat"},
                    {"from": "op_set_married",    "to": "op_merge_man"},
                    {"from": "op_merge_cat",      "to": "op_merge_man"},
                    {"from": "op_merge_man",      "to": "op_merge_woman"}
                ]
            }
        }
    }

    type_forest, places, transitions = jsons_to_objects(
        types_json, places_json, transitions_json
    )

    t = transitions["marry_and_adopt"]
    print(f"marry_and_adopt sensitized? {t.check_sensitization()}")
    if t.check_sensitization():
        consumed = t.consume_tokens(places)
        produced = t.produce_tokens()
        print(f"  consumed: {consumed}")
        print(f"  produced: {produced}")
    else:
        print("  cannot fire (missing inputs)")


if __name__ == "__main__":
    main()