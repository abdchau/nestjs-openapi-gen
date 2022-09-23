import re

class OptionsBuilder:
    def __init__(self):
        self.options = "{}"

    def add_option(self, key, value):
        comma = True if len(self.options) > 2 else False
        self.options = self.options[:-1] + f"{', ' if comma else ''}{key}: {value}" + "}"


def camel_to_hyphen(input):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', input).lower()

def DTO_import_builder(DTO_name, same_dir=False):
    return f"import {{ {DTO_name} }} from './{'' if same_dir else 'dto/'}{camel_to_hyphen(DTO_name[:-3])}.dto';"