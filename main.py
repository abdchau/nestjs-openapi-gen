import os
import shutil

from parsers.dto import DTOParser
from parsers.endpoint import EndpointParser

if __name__=='__main__':
    output_dir = './output'
    try:
        shutil.rmtree(output_dir)
    except:
        pass
    os.makedirs(output_dir, exist_ok=True)
    filename = './source/endpoint.json'
    s = input('Enter filename (default "./source/endpoint.json"): ')
    if s != '':
        filename = s

    req = int(input("""
    Enter 1 to generate DTO
    Enter 2 to generate endpoint
    """))

    if req == 1:
        DTO_name = input('Enter DTO to generate (default ALL DTOs): ')
        DTOParser(filename, output_dir).parse_file_DTO(DTO_name)
    elif req == 2:
        endpoint_name = input('Enter endpoint to generate (default ALL ENDPOINTS): ')
        EndpointParser(filename, output_dir).parse_file_endpoint(endpoint_name)

    print('\n...done')
