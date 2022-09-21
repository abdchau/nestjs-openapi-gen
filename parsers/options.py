class OptionsBuilder:
    def __init__(self):
        self.options = "{}"

    def add_option(self, key, value):
        comma = True if len(self.options) > 2 else False
        self.options = self.options[:-1] + f"{', ' if comma else ''}{key}: {value}" + "}"