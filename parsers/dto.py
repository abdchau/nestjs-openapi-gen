import json
import yaml
import re

from parsers.options import OptionsBuilder

class DTOParser:
    def __init__(self, filename, output_dir, curr_folder='') -> None:
        self.filename = filename
        self.base_folder = output_dir
        self.curr_folder = curr_folder

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
            self.parse_file_DTO(child_DTO_name)

        return f"\t@ApiProperty({options_builder.options}){ret}\n"

    def camel_to_hyphen(self, input):
        return re.sub(r'(?<!^)(?=[A-Z])', '-', input).lower()

    def parse_DTO(self, DTO, metadata):
        if DTO == 'IDDto':
            return
        dto_file_name = self.camel_to_hyphen(DTO[:-3])
        
        with open(f'{self.base_folder}/{self.curr_folder}{dto_file_name}.dto.ts', 'w') as f:
            f.write("import { ApiProperty } from '@nestjs/swagger';\n\n")
            f.write(f"export class {DTO} "+"{\n")
            
            if metadata['type'] == 'object':
                if 'properties' in metadata.keys():
                    for property in metadata.get('required', []):
                        metadata['properties'][property]['required'] = True
                    for property in metadata['properties']:
                        f.write(self.parse_property(property, metadata['properties'][property]))
            else:
                print('TYPE OF DTO IS NOT "object"')
            
            f.write("}\n")


    def parse_file_DTO(self, DTO_name):
        if 'yaml' in self.filename:
            with open(self.filename, 'r') as f:
                file_data = yaml.safe_load(f)
        else:
            with open(self.filename, 'r') as f:
                file_data = json.load(f)

        if DTO_name == '':
            for DTO in file_data['components']['schemas']:
                self.parse_DTO(DTO, file_data['components']['schemas'][DTO])
        else:
            self.parse_DTO(DTO_name, file_data['components']['schemas'][DTO_name])


if __name__=='__main__':
    DTOParser('./source/endpoint.json', './output').parse_file_DTO('')