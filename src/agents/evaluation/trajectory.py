import json

from .state import State


class Trajectory:
    def __init__(self, state_list: list[State]):
        self.states = state_list

    def add_state(self, state):
        self.states.append(state)

    def dump(self, save_path):
        """Dump the trajectory to a json file."""
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(
                [state.to_dict() for state in self.states],
                f,
                ensure_ascii=False,
                indent=4,
            )

    def to_list(self):
        return [state.to_dict() for state in self.states]

    @classmethod
    def load_from_json(cls, state_list_in_json):
        """Loads the trajectory from a JSON file."""
        state_list = []
        for state_json in state_list_in_json:
            state_list.append(State.load_from_json(state_json))
        return cls(state_list)
