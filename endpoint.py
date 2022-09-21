import json
from config import config
import os
from dto import DTOParser

class EndpointParser:
    def __init__(self) -> None:
        self.dto_parser = DTOParser()


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

    def parse_req_body(self, request_body: dict):
        request_body = request_body['content']['application/json']['schema']
        DTO_name: str = self.dto_parser.get_DTO_name(request_body['$ref'])
        self.dto_parser.parse_file_DTO(config.FNAME, DTO_name)

        return f"@Body() {DTO_name[0].lower()}{DTO_name[1:]}: {DTO_name}"

    def generate_signature(self, metadata):
        param_string = ''
        if 'parameters' in metadata.keys():
            param_strings = [self.parse_parameter(parameter) for parameter in metadata['parameters']]
            param_string = ', '.join(param_strings)

        body_string = ''
        if 'requestBody' in metadata.keys():
            body_string = self.parse_req_body(metadata['requestBody'])
            
        signature = f'funcName({param_string}{body_string})'
        return signature

    def get_annotation_endpoint(self, endpoint: str):
        tokens = endpoint.split('/')
        if '{' in tokens[-1]:
            return tokens[-1].replace('{', ':').replace('}', '')
        else:
            return tokens[-1]

    def parse_operation(self, endpoint: str, operation: str, metadata: dict):
        annotation = f"@{operation.capitalize()}('{self.get_annotation_endpoint(endpoint)}')"
        signature = self.generate_signature(metadata)

        return f"""
    {annotation}
    {signature} {{
        return this.myService.funcName();
    }}
    """

    def parse_endpoint(self, endpoint, metadata):
        config.CURRENT_FOLDER = endpoint.replace('/', '\\')+'/'
        os.makedirs(f'./output/{config.CURRENT_FOLDER}', exist_ok=True)
        for operation in metadata.keys():
            with open(f'./output/{config.CURRENT_FOLDER}name.controller.ts', 'a') as f:
                f.write(self.parse_operation(endpoint, operation, metadata[operation]))

        # print(metadata['post'])

    def parse_file_endpoint(self, filename, endpoint_name):
        with open(filename, 'r') as f:
            file_data = json.load(f)

        if endpoint_name == '':
            for endpoint in file_data['paths']:
                self.parse_endpoint(endpoint, file_data['paths'][endpoint])
        else:
            self.parse_endpoint(endpoint_name, file_data['paths'][endpoint_name])

if __name__=='__main__':
    EndpointParser().parse_file_endpoint('./source/endpoint.json', '')