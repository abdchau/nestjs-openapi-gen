import json
import yaml
import os

from parsers.dto import DTOParser

class EndpointParser:
    def __init__(self, filename, output_dir, file_data=None) -> None:
        self.filename = filename
        self.base_folder = output_dir
        self.curr_folder = self.base_folder
        self.file_data = file_data

        if self.file_data == None:
            if 'yaml' in self.filename:
                with open(self.filename, 'r') as f:
                    self.file_data = yaml.safe_load(f)
            else:
                with open(self.filename, 'r') as f:
                    self.file_data = json.load(f)

    # def get_default_pipe_string(self, parameter):
    #     default_pipe_string = ''

    #     default_type_value = {'string': "''", 'integer': 1}
    #     if parameter.get('required') == None:
    #         parameter['required'] = False

    #     if not parameter['required']:
    #         default_pipe_string = f", new DefaultValuePipe({default_type_value[parameter['schema']['type']]})"

    #     return default_pipe_string

    def parse_parameter(self, parameter: dict):
        in_dict = {'query': 'Query', 'path' : 'Param'}

        param_name = parameter['name']
        in_string = in_dict[parameter['in']]
        default_pipe_string = ''#self.get_default_pipe_string(parameter)
        param_type = 'number' if parameter['schema']['type'] =='integer' else parameter['schema']['type']
        param_string = f"@{in_string}('{param_name}'{default_pipe_string}) {param_name}: {param_type}"

        if parameter.get('required') == None:
            parameter['required'] = False
        
        return param_string, param_name, param_type, parameter['required']

    def parse_req_body(self, request_body: dict, dto_parser: DTOParser):
        request_body = request_body['content']['application/json']['schema']
        DTO_name: str = dto_parser.get_DTO_name(request_body['$ref'])
        dto_parser.parse_file_DTO(DTO_name)

        arg_name = f"{DTO_name[0].lower()}{DTO_name[1:]}"
        return f"@Body() {arg_name}: {DTO_name}", arg_name, DTO_name 

    def generate_signature(self, metadata, func_name: str, dto_parser: DTOParser):
        args = []
        arg_types = []
        query_not_required = []
        param_string = ''
        if 'parameters' in metadata.keys():
            param_strings = []
            for parameter in metadata['parameters']:
                p_string, arg_name, arg_type, required = self.parse_parameter(parameter)
                if not required:
                    query_not_required.append(f"'{arg_name}'")
                param_strings.append(p_string)
                args.append(arg_name)
                arg_types.append(arg_type)
            param_string = ', '.join(param_strings)

        body_string = ''
        if 'requestBody' in metadata.keys():
            if param_string != '':
                body_string = ", "
            b_string, arg_name, arg_type = self.parse_req_body(metadata['requestBody'], dto_parser)
            body_string += b_string
            args.append(arg_name)
            arg_types.append(arg_type)

        signature = f'{func_name}({param_string}{body_string})'
        return signature, args, arg_types, query_not_required

    def get_annotation_endpoint(self, endpoint: str):
        if endpoint.count('/') == 1:
            return ''
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
            jwt_string = "@Public()\n\t"
        elif options['jwt'] != 'true':
            raise Exception('jwt argument in summary is not correct')

        roles_string = ''
        for role in options['roles'].split(','):
            roles_string += f', Role.{role.capitalize()}'
        roles_string = roles_string[2:]
        
        options_string = f"""
    {jwt_string}@Roles({roles_string})"""

        return options_string        

    def parse_response_dto(self, response_object: dict, dto_parser: DTOParser):
        DTO_names = []
        try:
            response_object = response_object['content']['application/json']['schema']
        except:
            return DTO_names

        if response_object.get('type') == "array":
            if response_object['items'].get('$ref', None) == None:
                return DTO_names
            DTO_name: str = dto_parser.get_DTO_name(response_object['items']['$ref'])
            dto_parser.parse_file_DTO(DTO_name)
            DTO_names.append('['+DTO_name+']')
        elif '$ref' in response_object:
            DTO_name: str = dto_parser.get_DTO_name(response_object['$ref'])
            dto_parser.parse_file_DTO(DTO_name)
            DTO_names.append(DTO_name)
        else:
            for property in response_object['properties']:
                if '$ref' in response_object['properties'][property]:
                    DTO_name: str = dto_parser.get_DTO_name(response_object['properties'][property]['$ref'])
                    dto_parser.parse_file_DTO(DTO_name)
                    DTO_names.append("Pagination"+DTO_name)
                        

        return DTO_names

    def parse_response(self, response_code, metadata, dto_parser: DTOParser):
        DTO_names = self.parse_response_dto(metadata, dto_parser)
        type_string = ""
        for dto_name in DTO_names:
            type_string += f"\n\t\ttype: {dto_name},"

        return f"""@ApiResponse({{
        status: {response_code},{type_string}
    }})"""

    def parse_operation(self, endpoint: str, operation: str, metadata: dict, dto_parser: DTOParser):
        controller_name = metadata.get('tags', ['default'])[0]
        auths = self.parse_summary(metadata.get('summary', ''))
        operation_annotation = f"@{operation.capitalize()}('{self.get_annotation_endpoint(endpoint)}')"
        func_name = metadata.get('operationId', 'funcName')
        if '_' in func_name:
            func_name = func_name.split('_')[-1]

        signature, args, arg_types, query_not_required = self.generate_signature(metadata, func_name, dto_parser)
        service_signature = []
        for i in range(len(args)):
            service_signature.append(f"{args[i]}: {arg_types[i]}")

        response_string = ''
        for response_code in metadata['responses']:
            response_string += self.parse_response(response_code, metadata['responses'][response_code], dto_parser)

        query_not_required_string = '' if len(query_not_required) == 0 else f"\n\t@QueryNotRequired([{', '.join(query_not_required)}])"

        return f"""
    {auths}
    {response_string}{query_not_required_string}
    {operation_annotation}
    {signature} {{
        // {func_name}({', '.join(service_signature)}) {{}}
        return this.{controller_name}Service.{func_name}({', '.join(args)});
    }}"""

    def parse_endpoint(self, endpoint, metadata):
        self.curr_folder = endpoint.replace('/', '\\')+'/'
        endpoint_dir = f'{self.base_folder}/{self.curr_folder}'
        os.makedirs(endpoint_dir, exist_ok=True)

        dto_parser = DTOParser(self.filename, self.base_folder, self.curr_folder, file_data=self.file_data)
        for operation in metadata.keys():
            with open(f'{endpoint_dir}name.controller.ts', 'a') as f:
                f.write(self.parse_operation(endpoint, operation, metadata[operation], dto_parser))


    def parse_file_endpoint(self, endpoint_name=''):
        if endpoint_name == '':
            for endpoint in self.file_data['paths']:
                self.parse_endpoint(endpoint, self.file_data['paths'][endpoint])
        else:
            self.parse_endpoint(endpoint_name, self.file_data['paths'][endpoint_name])


if __name__=='__main__':
    EndpointParser('./source/endpoint.json', './output').parse_file_endpoint('')