import json
import yaml
import os

from parsers.endpoint import EndpointParser
from parsers.folder import FolderParser

class ControllerParser:
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

    def parse_controller(self, controller, controller_endpoints):
        self.curr_folder = controller

        controller_dir = f'{self.base_folder}/{self.curr_folder}'
        os.makedirs(controller_dir, exist_ok=True)

        endpoint_parser = EndpointParser(self.filename, controller_dir, file_data=self.file_data)

        controller_DTOs = set()
        for endpoint in controller_endpoints:
            endpoint_DTOs = set(endpoint_parser.parse_file_endpoint(endpoint))
            controller_DTOs.update(endpoint_DTOs)

        return controller_DTOs

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

        if controller_name == '':
            for controller in self.get_all_tags(self.file_data):
                controller_DTOs = self.parse_controller(controller, self.get_controller_metadata(controller, self.file_data))
                FolderParser(f'{self.base_folder}/{self.curr_folder}', controller_DTOs).parse_folder()
        else:
            controller_DTOs = self.parse_controller(controller_name, self.get_controller_metadata(controller_name, self.file_data))
            FolderParser(f'{self.base_folder}/{self.curr_folder}', controller_DTOs).parse_folder()