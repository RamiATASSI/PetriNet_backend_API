from typing import Any


class Place:
    def __init__(self, place_name, place_data: dict, colors: dict[str, Any]):
        self.place_name: str = place_name
        self.tokens: dict[str, int] = {}
        self.action: dict[str, str] = {}
        self.colors: dict[str, Any] = colors

        for color, data in place_data.items():
            try:
                print(f"Initializing tokens and actions for color: {color}")
                self.tokens[color] = data.get('Tokens_nbr', 0)  # Default to 0 if missing
                self.action[color] = data.get('Action', None)  # Default to None if missing
            except Exception as e:
                raise Exception(f"Error initializing color {color}: {e}")

    def get_colors(self) -> set[str]:
        return {key for key, value in self.tokens.items() if value > 0}

    def add_colored_tokens(self, color: str, token_count: int) -> None:
        if color in self.tokens:
            self.tokens[color] += token_count
        else:
            self.tokens[color] = token_count

    def select_color_function_as_place_action(self, color: str, function_name: str) -> None:
        self.action[color] = function_name

    def launch_action(self, color: str, args=None) -> Any:
        if args is None:
            return getattr(self.colors[color], self.action[color])()
        else:
            return getattr(self.colors[color], self.action[color])(**args)

    def describe(self) -> None:
        print("Place name: ", self.place_name)
        print("Tokens: ", self.tokens)
        print("Actions: ", self.action)
        print()

    def __str__(self) -> str:
        return self.place_name
