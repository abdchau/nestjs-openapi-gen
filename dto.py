import json
from config import FNAME

def get_DTO_name(s: str):
    return s.split('/')[-1]

def get_ts_type(tipe):
    return 'number' if tipe == 'integer' else tipe

def parse_property(property, metadata):
    ret = ''

    child_DTO_name = ''

    if metadata.get('$ref', None) != None:
        child_DTO_name = get_DTO_name(metadata['$ref'])
        ret = f"""
    @ApiProperty()
    {property}: {child_DTO_name};
"""

    elif metadata['type'] != 'array':
        ret = f"""
    @ApiProperty()
    {property}: {get_ts_type(metadata['type'])};
"""


    else:


        if metadata['items'].get('$ref', None) != None:
            child_DTO_name = get_DTO_name(metadata['items']['$ref'])
            ret = f"""
    @ApiProperty({{
        isArray: true,
        type: {child_DTO_name},
    }})
    {property}: {child_DTO_name}[];
"""

        else:
            tipe = get_ts_type(metadata['items']['type'])
            ret = f"""
    @ApiProperty({{
        isArray: true,
        type: {tipe},
    }})
    {property}: {tipe}[];
"""

    if child_DTO_name != '':
        parse_file_DTO(FNAME, child_DTO_name)

    return ret

def parse_DTO(DTO, metadata):
    with open(f'./output/{DTO}.dto.ts', 'w') as f:
        f.write("import { ApiProperty } from '@nestjs/swagger';\n\n")
        f.write(f"export class {DTO} "+"{\n")
        
        if metadata['type'] == 'object':
            for property in metadata['properties']:
                f.write(parse_property(property, metadata['properties'][property]))
        else:
            print('TYPE OF DTO IS NOT "object"')
        
        f.write("}\n")


def parse_file_DTO(filename, DTO_name):
    global FNAME
    FNAME = filename
    with open(FNAME, 'r') as f:
        file_data = json.load(f)

    if DTO_name == '':
        for DTO in file_data['components']['schemas']:
            parse_DTO(DTO, file_data['components']['schemas'][DTO])
    else:
        parse_DTO(DTO_name, file_data['components']['schemas'][DTO_name])


if __name__=='__main__':
    parse_file_DTO('./source/endpoint.json', '')