import os
import shutil

from parsers.helpers import DTO_import_builder

class FolderParser:
    def __init__(self, controller_dir, controller_DTOs) -> None:
        self.controller_dir = controller_dir
        self.controller_DTOs = list(controller_DTOs)
        try:
            self.controller_DTOs.remove('IDDto')
        except:
            pass

    def parse_dto_files(self, from_dir, to_dir, dto_files):
        if dto_files is None:
            return
        os.makedirs(to_dir, exist_ok=True)
        for dto_file in dto_files:
            # try:
            shutil.move(os.path.join(from_dir, dto_file), os.path.join(to_dir, dto_file))
            # except Exception as e:
            # print(e)

    def write_controller(self, controller_name, controller_code, controller_code_file, DTO_imports_string):
        controller_class_name = "".join([token.capitalize() for token in controller_name.split('-')])

        with open(os.path.join(self.controller_dir, controller_code_file), 'w') as f:
            f.write(f"""import {{
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  UseGuards,
  Query,
}} from '@nestjs/common';
import {{ ApiQuery, ApiResponse, ApiBearerAuth, ApiTags }} from '@nestjs/swagger';

import {{ {controller_name.capitalize()}Service }} from './{controller_name}.service';

import {{ Public }} from '../../../auth/decorators/jwt-auth.decorator';
import {{ Roles }} from '../../../auth/decorators/roles.decorator';
import {{ Role }} from '../../../auth/role.enum';

import {{ QueryNotRequired }} from '../../../common/decorators/query-not-required.decorator';
import {{ ApiPaginatedResponse }} from '../../../common/responses/api-paginated-response.response';
import {{ ApiRecordsResponse }} from '../../../common/responses/api-records-response.response';

import {{ IDDto }} from '../../../common/dtos/id.dto';
{DTO_imports_string}

@Controller('{controller_name}')
@ApiTags('{controller_name}')
export class {controller_class_name}Controller {{
    constructor(private {controller_name}Service: {controller_name.capitalize()}Service) {{}}""")
            f.write(controller_code)
            f.write("\n}\n")
        



    # ================================================================================================
    # ================================================================================================
    # ================================================================================================
    # ================================================================================================
    # ================================================================================================



    def write_service(self, service_name, service_code, service_code_file, DTO_imports_string):
        service_class_name = "".join([token.capitalize() for token in service_name.split('-')])

        with open(os.path.join(self.controller_dir, service_code_file), 'w') as f:
            f.write(f"""import {{ Injectable }} from '@nestjs/common';

import {{ PrismaService }} from '../../../prisma/prisma.service';
import {{
  MakeTimedIDUnique,
  unix_timestamp,
}} from '../../../common/helpers.common';

{DTO_imports_string}

@Injectable()
export class {service_class_name}Service {{
    constructor(private prisma: PrismaService) {{}}\n""")
            f.write(service_code)
            f.write("}\n")


    def parse_folder(self):
        # generate DTO imports
        DTO_imports_string = '\n'.join([DTO_import_builder(DTO_name) for DTO_name in self.controller_DTOs])

        # handle code and DTO files
        controller_code = ""
        service_code = ""
        for endpoint_dir in os.listdir(self.controller_dir):
            controller_code_file_name = 'name.controller.ts'
            service_code_file_name = 'name.service.ts'

            # handle DTOs
            endpoint_dir = f'{self.controller_dir}/{endpoint_dir}'
            dto_files = os.listdir(endpoint_dir)
            dto_files.remove(controller_code_file_name)
            dto_files.remove(service_code_file_name)
            
            self.parse_dto_files(endpoint_dir, f'{self.controller_dir}/dto', dto_files)

            # handle controller_code_file_name
            with open(os.path.join(endpoint_dir, controller_code_file_name)) as f:
                controller_code += f.read()
            with open(os.path.join(endpoint_dir, service_code_file_name)) as f:
                service_code += f.read()
        

        controller_name = self.controller_dir.split('/')[-1]
        controller_code_file = f"{controller_name}.controller.ts"
        service_code_file = f"{controller_name}.service.ts"

        self.write_controller(controller_name, controller_code, controller_code_file, DTO_imports_string)
        self.write_service(controller_name, service_code, service_code_file, DTO_imports_string)
        

        controller_folders = os.listdir(self.controller_dir)
        controller_folders.remove('dto')
        controller_folders.remove(controller_code_file)
        controller_folders.remove(service_code_file)
        for folder in controller_folders:
            shutil.rmtree(os.path.join(self.controller_dir, folder))
