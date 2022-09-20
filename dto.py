import json


def get_DTO_name(s: str):
    return s.split('/')[-1]

def parse_property(property, metadata):
    ret = ''
    if metadata['type'] != 'array':
        ret = f"""
    @ApiProperty()
    {property}: {metadata['type']};
"""
    else:
        property_DTO_name = get_DTO_name(metadata['items']['$ref'])
        ret = f"""
    @ApiProperty({{
        isArray: true,
        type: {property_DTO_name},
    }})
    {property}: {property_DTO_name}[];
"""

    print(property)
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
    with open(filename, 'r') as f:
        file_data = json.load(f)

    if DTO_name == '':
        for DTO in file_data['components']['schemas']:
            parse_DTO(DTO, file_data['components']['schemas'][DTO])
    else:
        parse_DTO(DTO_name, file_data['components']['schemas'][DTO_name])


if __name__=='__main__':
    parse_file_DTO('./source/endpoint.json', '')