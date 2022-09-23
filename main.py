import os
import shutil
import json
import yaml

from parsers.controller import ControllerParser
from parsers.dto import DTOParser
from parsers.endpoint import EndpointParser

if __name__=='__main__':
    output_dir = './output'
    try:
        shutil.rmtree(output_dir)
    except:
        pass
    os.makedirs(output_dir, exist_ok=True)
    filename = './source/spec'
    s = input(f'Enter filename WITHOUT extension (default "{filename}"): ')
    if s != '':
        filename = s

    file_data = None
    try:
        try:
            with open(filename+'.yaml', 'r') as f:
                file_data = yaml.safe_load(f)
                filename += '.yaml'
        except:
            with open(filename+'.json', 'r') as f:
                file_data = json.load(f)
                filename += '.json'
    except FileNotFoundError:
        print('File not found')
        exit()
    except:
        print('File could not be parsed')
        exit()


    req = int(input("""
    Enter 1 to generate DTO
    Enter 2 to generate endpoint
    Enter 3 to generate controller
    """))

    if req == 1:
        DTO_name = input('Enter DTO to generate (default ALL DTOs): ')
        DTOParser(filename, output_dir, file_data=file_data).parse_file_DTO(DTO_name)
    elif req == 2:
        endpoint_name = input('Enter endpoint to generate (default ALL ENDPOINTS): ')
        EndpointParser(filename, output_dir, file_data=file_data).parse_file_endpoint(endpoint_name)
    elif req == 3:
        controller_name = input('Enter controller (tag) to generate (default ALL CONTROLLERS): ')
        ControllerParser(filename, output_dir, file_data=file_data).parse_file_controller(controller_name)

    print('\n...done')
