import json
import os
from parsers.dto import DTOParser
from parsers.options import OptionsBuilder

class EndpointParser:
    def __init__(self, filename, output_dir) -> None:
        self.filename = filename
        self.base_folder = output_dir
        self.curr_folder = self.base_folder

    def get_default_pipe_string(self, parameter):
        default_pipe_string = ''

        default_type_value = {'string': "''", 'integer': 1}
        if parameter.get('required') == None:
            parameter['required'] = True

        if not parameter['required']:
            default_pipe_string = f", new DefaultValuePipe({default_type_value[parameter['schema']['type']]})"

        return default_pipe_string

    def parse_parameter(self, parameter: dict):
        in_dict = {'query': 'Query', 'path' : 'Param'}

        param_name = parameter['name']
        in_string = in_dict[parameter['in']]
        default_pipe_string = self.get_default_pipe_string(parameter)
        param_type = parameter['schema']['type']
        param_string = f"@{in_string}('{param_name}'{default_pipe_string}) {param_name}: {param_type}"

        return param_string

    def parse_req_body(self, request_body: dict, dto_parser: DTOParser):
        request_body = request_body['content']['application/json']['schema']
        DTO_name: str = dto_parser.get_DTO_name(request_body['$ref'])
        dto_parser.parse_file_DTO(DTO_name)

        return f"@Body() {DTO_name[0].lower()}{DTO_name[1:]}: {DTO_name}"

    def generate_signature(self, metadata, func_name: str, dto_parser: DTOParser):
        param_string = ''
        if 'parameters' in metadata.keys():
            param_strings = [self.parse_parameter(parameter) for parameter in metadata['parameters']]
            param_string = ', '.join(param_strings)

        body_string = ''
        if 'requestBody' in metadata.keys():
            body_string = self.parse_req_body(metadata['requestBody'], dto_parser)
            
        signature = f'{func_name}({param_string}{body_string})'
        return signature

    def get_annotation_endpoint(self, endpoint: str):
        tokens = endpoint.split('/')
        if '{' in tokens[-1]:
            return tokens[-1].replace('{', ':').replace('}', '')
        else:
            return tokens[-1]


    def parse_summary(self, summary: str):
        # "jwt = true; roles = Admin, Doctor;"
        if summary == '':
            return ''
        if summary[-1] == ';':
            summary = summary[:-1]
        summary = "".join(summary.split())
        tokens = [token.split('=') for token in summary.lower().split(';')]
        options = {token[0]: token[1] for token in tokens}
        
        jwt_string = ''
        if options['jwt'] == 'false':
            jwt_string = "@Public()"
        elif options['jwt'] != 'true':
            raise Exception('jwt argument in summary is not correct')

        roles_string = ''
        for role in options['roles'].split(','):
            roles_string += f', Role.{role.capitalize()}'
        roles_string = roles_string[2:]
        
        options_string = f"""
    {jwt_string}
    @Roles({roles_string})"""

        return options_string        
        

    def parse_operation(self, endpoint: str, operation: str, metadata: dict, dto_parser: DTOParser):
        auths = self.parse_summary(metadata.get('summary', ''))
        annotation = f"@{operation.capitalize()}('{self.get_annotation_endpoint(endpoint)}')"
        func_name = metadata.get('operationId', 'funcName')
        if '_' in func_name:
            func_name = func_name.split('_')[-1]

        signature = self.generate_signature(metadata, func_name, dto_parser)

        return f"""
    {auths}
    {annotation}
    {signature} {{
        return this.myService.{func_name}();
    }}
    """

    def parse_endpoint(self, endpoint, metadata):
        self.curr_folder = endpoint.replace('/', '\\')+'/'
        os.makedirs(f'{self.base_folder}/{self.curr_folder}', exist_ok=True)

        dto_parser = DTOParser(self.filename, self.base_folder, self.curr_folder)
        for operation in metadata.keys():
            with open(f'{self.base_folder}/{self.curr_folder}name.controller.ts', 'a') as f:
                f.write(self.parse_operation(endpoint, operation, metadata[operation], dto_parser))

        # print(metadata['post'])

    def parse_file_endpoint(self, endpoint_name):
        with open(self.filename, 'r') as f:
            file_data = json.load(f)

        if endpoint_name == '':
            for endpoint in file_data['paths']:
                self.parse_endpoint(endpoint, file_data['paths'][endpoint])
        else:
            self.parse_endpoint(endpoint_name, file_data['paths'][endpoint_name])

if __name__=='__main__':
    EndpointParser('./source/endpoint.json', './output').parse_file_endpoint('')