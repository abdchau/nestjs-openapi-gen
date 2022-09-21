import os
import shutil

class FolderParser:
    def __init__(self, controller_dir) -> None:
        self.controller_dir = controller_dir

    def parse_dto_files(self, from_dir, to_dir, dto_files):
        if dto_files is None:
            return
        os.makedirs(to_dir, exist_ok=True)
        for dto_file in dto_files:
            # try:
            shutil.move(os.path.join(from_dir, dto_file), os.path.join(to_dir, dto_file))
            # except Exception as e:
            # print(e)
                
        

    def parse_folder(self):
        controller_code = ""
        for endpoint_dir in os.listdir(self.controller_dir):
            code_file_name = 'name.controller.ts'

            # handle DTOs
            endpoint_dir = f'{self.controller_dir}/{endpoint_dir}'
            dto_files = os.listdir(endpoint_dir)
            dto_files.remove(code_file_name)
            
            self.parse_dto_files(endpoint_dir, f'{self.controller_dir}/dtos', dto_files)

            # handle code_file_name
            with open(os.path.join(endpoint_dir, code_file_name)) as f:
                controller_code += f.read()
        
        controller_name = self.controller_dir.split('/')[-1]
        controller_code_file = f"{controller_name}.controller.ts"

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
}} from '@nestjs/common';
import {{ ApiBearerAuth, ApiTags }} from '@nestjs/swagger';

import {{ Public }} from '../../../auth/decorators/jwt-auth.decorator';
import {{ Roles }} from '../../../auth/decorators/roles.decorator';
import {{ Role }} from '../../../auth/role.enum';

@Controller('{controller_name}')
@ApiTags('{controller_name}')
export class {controller_class_name}Controller {{
    constructor() {{}}""")
            f.write(controller_code)
            f.write("}\n")

        controller_folders = os.listdir(self.controller_dir)
        controller_folders.remove('dtos')
        controller_folders.remove(controller_code_file)
        for folder in controller_folders:
            shutil.rmtree(os.path.join(self.controller_dir, folder))
