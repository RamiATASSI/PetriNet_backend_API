from src.PetriNet_algo.object.token import TypeForest


class TypeForestDeserializer:
    """
    Builds a TypeForest (hierarchical token type forest) from JSON data.
    Expects JSON mapping type names to optional parent names:
      {
        "TypeA": {"parent": None},
        "SubType": {"parent": "TypeA"},
        ...
      }
    """

    def __init__(self):
        self.forest = TypeForest()

    def compile(self, types_json: dict[str, dict[str, str | None]]) -> TypeForest:
        pending = set(types_json.keys())
        while pending:
            progress = False
            for tname in list(pending):
                parent = types_json[tname].get("parent")
                if parent is None or parent in self.forest._nodes:
                    # register the type under its parent (None for a root)
                    self.forest.add_type(tname, parent)
                    pending.remove(tname)
                    progress = True
            if not progress:
                raise ValueError(
                    f"Cyclic or missing parent reference in types JSON: {pending}"
                )
        return self.forest



def main() -> None:
    """
    Usage example: build and print a TypeForest for
    LivingBeing -> {Human -> {Man, Woman}, Animal -> {Cat, Dog}}
    Family
    PolarMolecules -> {H2O -> {2_Hydrogen, 1_Oxygen}, HCl -> {1_Hydrogen, 1_Chloride}}
    """

    types_json = {
        "LivingBeing": {"parent": None},
        "Human":       {"parent": "LivingBeing"},
        "Animal":      {"parent": "LivingBeing"},
        "Man":         {"parent": "Human"},
        "Woman":       {"parent": "Human"},
        "Cat":         {"parent": "Animal"},
        "Dog":         {"parent": "Animal"},

        "Family":      {"parent": None},


        "PolarMolecules":   {"parent": None},
        "H2O":              {"parent": "PolarMolecules"},
        "HCl":              {"parent": "PolarMolecules"},
        "2_Hydrogen":       {"parent": "H2O"},
        "1_Oxygen":         {"parent": "H2O"},
        "1_Hydrogen":       {"parent": "HCl"},
        "1_Chloride":       {"parent": "HCl"},

    }

    deserializer = TypeForestDeserializer()
    forest = deserializer.compile(types_json)

    # display each type and its parent
    print("TypeForest:")
    for type_name, node in forest._nodes.items():
        parent_name = node.parent.name if node.parent is not None else None
        print(f"  {type_name} has parent: {parent_name}")


if __name__ == "__main__":
    main()