import json
from config import FNAME
from dto import get_DTO_name, parse_file_DTO

def get_default_pipe_string(parameter):
    default_pipe_string = ''

    default_type_value = {'string': "''", 'integer': 1}
    if parameter.get('required') == None:
        parameter['required'] = True

    if not parameter['required']:
        default_pipe_string = f", new DefaultValuePipe({default_type_value[parameter['schema']['type']]})"

    return default_pipe_string

def parse_parameter(parameter: dict):
    in_dict = {'query': 'Query'}
    # print(json.dumps(parameter, indent=2))

    param_name = parameter['name']
    in_string = in_dict[parameter['in']]
    default_pipe_string = get_default_pipe_string(parameter)
    param_type = parameter['schema']['type']
    param_string = f"@{in_string}('{param_name}'{default_pipe_string}) {param_name}: {param_type}"

    return param_string

def parse_req_body(request_body: dict):
    request_body = request_body['content']['application/json']['schema']
    DTO_name: str = get_DTO_name(request_body['$ref'])
    parse_file_DTO(FNAME, DTO_name)

    print(json.dumps(request_body, indent=2))
    return f"@Body() {DTO_name[0].lower()}{DTO_name[1:]}: {DTO_name}"

def generate_signature(metadata):
    param_string = ''
    if 'parameters' in metadata.keys():
        param_strings = [parse_parameter(parameter) for parameter in metadata['parameters']]
        param_string = ', '.join(param_strings)

    body_string = ''
    if 'requestBody' in metadata.keys():
        body_string = parse_req_body(metadata['requestBody'])
        
    signature = f'funcName({param_string}{body_string})'
    return signature

def parse_operation(endpoint: str, operation: str, metadata: dict):
    # print(operation.capitalize())
    # print(metadata.keys())
    
    annotation = f'@{operation.capitalize()}()'
    # params = f''
    
    signature = generate_signature(metadata)
    print(annotation)
    print(signature)
    print()

    dummy = \
    """
    @Get()
    fetchAll(@Query('search', new DefaultValuePipe('')) searchString: string) {
        return this.journalTypesService.fetchAll(searchString);
    }
    """

def parse_endpoint(endpoint, metadata):
    for operation in metadata.keys():
        parse_operation(endpoint, operation, metadata[operation])

    # print(metadata['post'])

def parse_file_endpoint(filename, endpoint_name):
    with open(filename, 'r') as f:
        file_data = json.load(f)

    if endpoint_name == '':
        for endpoint in file_data['paths']:
            parse_endpoint(endpoint, file_data['paths'][endpoint])
    else:
        parse_endpoint(endpoint_name, file_data['paths'][endpoint_name])

if __name__=='__main__':
    parse_file_endpoint('./source/endpoint.json', '')