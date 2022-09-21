import os
import shutil

from config import config
from dto import DTOParser
from endpoint import EndpointParser

if __name__=='__main__':
    try:
        shutil.rmtree('./output')
    except:
        pass
    os.makedirs('./output', exist_ok=True)
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
        DTOParser(filename).parse_file_DTO(DTO_name)
    elif req == 2:
        endpoint_name = input('Enter endpoint to generate (default ALL ENDPOINTS): ')
        EndpointParser(filename).parse_file_endpoint(endpoint_name)

    print('\n...done')
