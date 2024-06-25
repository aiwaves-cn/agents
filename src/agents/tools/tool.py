from abc import abstractmethod


class Tool:
    def __init__(self, description, name, parameters):
        self.type = "function"
        self.description = description  # A description of what the function does, used by the model to choose when and how to call the function.
        self.name = name  # The name of the function to be called. Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length of 64.
        self.parameters = parameters  # The parameters the functions accepts, described as a JSON Schema object. See the guide for examples, and the JSON Schema reference for documentation about the format. Omitting parameters defines a function with an empty parameter list.

    @abstractmethod
    def func(self):
        pass

    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def load_from_dict(cls, dict_data):
        pass
