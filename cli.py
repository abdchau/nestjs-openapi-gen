import os

from config import config
from dto import parse_file_DTO
from endpoint import parse_file_endpoint

if __name__=='__main__':
    os.makedirs('output', exist_ok=True)
    s = input('Enter filename (default "./source/endpoint.json"): ')
    if s != '':
        config.FNAME = s

    req = int(input("""
    Enter 1 to generate DTO
    Enter 2 to generate endpoint
    """))

    if req == 1:
        DTO_name = input('Enter DTO to generate (default ALL DTOs): ')
        parse_file_DTO(config.FNAME, DTO_name)
    elif req == 2:
        endpoint_name = input('Enter endpoint to generate (default ALL ENDPOINTS): ')
        parse_file_endpoint(config.FNAME, endpoint_name)

