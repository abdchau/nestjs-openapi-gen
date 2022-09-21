import json
import os

from parsers.endpoint import EndpointParser
from parsers.folder import FolderParser

class ControllerParser:
    def __init__(self, filename, output_dir) -> None:
        self.filename = filename
        self.base_folder = output_dir
        self.curr_folder = self.base_folder


    def parse_controller(self, controller, controller_endpoints):
        self.curr_folder = controller

        controller_dir = f'{self.base_folder}/{self.curr_folder}'
        os.makedirs(controller_dir, exist_ok=True)

        endpoint_parser = EndpointParser(self.filename, controller_dir)

        for endpoint in controller_endpoints:
            endpoint_parser.parse_file_endpoint(endpoint)

    def get_controller_metadata(self, controller, file_data):
        controller_endpoints = set()
        for path in file_data['paths']:
            of_interest = False
            for operation in file_data['paths'][path]:
                operation_tags = file_data['paths'][path][operation].get('tags', ['default'])
                if operation_tags[0] == controller:
                    of_interest = True
            if of_interest:
                controller_endpoints.add(path)

        return controller_endpoints

    def get_all_tags(self, file_data):
        tags = set()
        for path in file_data['paths']:
            for operation in file_data['paths'][path]:
                tags.add(file_data['paths'][path][operation].get('tags', ['default'])[0])

        return tags

    def parse_file_controller(self, controller_name):
        with open(self.filename, 'r') as f:
            file_data = json.load(f)

        if controller_name == '':
            for controller in self.get_all_tags(file_data):
                self.parse_controller(controller, self.get_controller_metadata(controller, file_data))
                FolderParser(f'{self.base_folder}/{self.curr_folder}').parse_folder()
        else:
            self.parse_controller(controller_name, self.get_controller_metadata(controller_name, file_data))
            FolderParser(f'{self.base_folder}/{self.curr_folder}').parse_folder()