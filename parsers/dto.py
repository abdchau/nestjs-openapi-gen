import json
import yaml

from parsers.helpers import OptionsBuilder, camel_to_hyphen, DTO_import_builder

class DTOParser:
    def __init__(self, filename, output_dir, curr_folder='', file_data=None) -> None:
        self.filename = filename
        self.base_folder = output_dir
        self.curr_folder = curr_folder
        self.file_data = file_data
        self.child_DTO_names = []

        if self.file_data == None:
            if 'yaml' in self.filename:
                with open(self.filename, 'r') as f:
                    self.file_data = yaml.safe_load(f)
            else:
                with open(self.filename, 'r') as f:
                    self.file_data = json.load(f)

    def get_DTO_name(self, s: str):
        return s.split('/')[-1]

    def get_ts_type(self, tipe):
        return 'number' if tipe == 'integer' else tipe

    def parse_property(self, property, metadata):
        options_builder = OptionsBuilder()
        if metadata.get('required', False):
            options_builder.add_option('required', 'true')
        else:
            options_builder.add_option('required', 'false')
            property += "?"

        ret = ""
        child_DTO_name = ''

        if metadata.get('$ref', None) != None:
            child_DTO_name = self.get_DTO_name(metadata['$ref'])
            self.child_DTO_names.append(child_DTO_name)
            ret = f"""
    {property}: {child_DTO_name};
"""

        elif metadata['type'] != 'array':
            ret = f"""
    {property}: {self.get_ts_type(metadata['type'])};
"""


        else:

            options_builder.add_option("isArray", "true")
            if metadata['items'].get('$ref', None) != None:
                child_DTO_name = self.get_DTO_name(metadata['items']['$ref'])
                self.child_DTO_names.append(child_DTO_name)
                options_builder.add_option("type",  child_DTO_name)
                ret = f"""
    {property}: {child_DTO_name}[];
"""

            else:
                tipe = self.get_ts_type(metadata['items']['type'])
                options_builder.add_option("type", tipe)
                ret = f"""
    {property}: {tipe}[];
"""

        if child_DTO_name != '':
            DTOParser(self.filename, self.base_folder, self.curr_folder, self.file_data).parse_file_DTO(child_DTO_name)

        return f"  @ApiProperty({ options_builder.options }){ret}\n"

    def parse_DTO(self, DTO, metadata):
        if DTO == 'IDDto':
            return
        dto_file_name = camel_to_hyphen(DTO[:-3])
        
        properties_string = ''
        if metadata['type'] == 'object':
            if 'properties' in metadata.keys():
                    for property in metadata.get('required', []):
                        metadata['properties'][property]['required'] = True
                    for property in metadata['properties']:
                        properties_string += self.parse_property(property, metadata['properties'][property])
        else:
            print(DTO, 'TYPE OF DTO IS NOT "object"')

        DTO_imports_string = '\n'.join([DTO_import_builder(DTO_name, same_dir=True) for DTO_name in self.child_DTO_names])
        with open(f'{self.base_folder}/{self.curr_folder}{dto_file_name}.dto.ts', 'w') as f:
            f.write("import { ApiProperty } from '@nestjs/swagger';\n")
            f.write(DTO_imports_string)
            f.write(f"\n\nexport class {DTO} "+"{\n")
            f.write(properties_string)
            f.write("}\n")


    def parse_file_DTO(self, DTO_name):
        if DTO_name == '':
            for DTO in self.file_data['components']['schemas']:
                self.parse_DTO(DTO, self.file_data['components']['schemas'][DTO])
        else:
            self.parse_DTO(DTO_name, self.file_data['components']['schemas'][DTO_name])


if __name__=='__main__':
    DTOParser('./source/endpoint.json', './output').parse_file_DTO('')