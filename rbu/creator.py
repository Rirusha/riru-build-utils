'''
Copyright (C) 2025 Vladimir Vaskov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

SPDX-License-Identifier: GPL-3.0-or-later
'''


import os
import shutil
from rbu.utils import Constants, ask, print_on_no


class Creator:

    language:str
    project_type:str
    
    def __init__(self, language:str, project_type:str):
        self.language = language
        self.project_type = project_type
        
    def create(self):
        templates_dir = os.path.join(Constants.PKGDATADIR, 'spec-templates')
        
        if self.language not in os.listdir(templates_dir):
            raise ValueError(f'Language \'{self.language}\' not supported. Supported languages: {', '.join(os.listdir(templates_dir))}')
        
        language_dir = os.path.join(templates_dir, self.language)

        if self.project_type not in os.listdir(language_dir):
            raise ValueError(f'Project type \'{self.project_type}\' not supported. Supported types: {', '.join(os.listdir(language_dir))}')
        
        spec_path = os.path.join(language_dir, self.project_type)
        create_spec_path = os.path.join(os.path.curdir, 'build-aux', 'sisyphus', 'template.spec')
        
        if os.path.exists(create_spec_path):
            print('Spec file \'{create_spec_path}\' already exists.')
            if not ask('Overwrite?'):
                print_on_no()
                return

            shutil.rmtree(create_spec_path)

        shutil.copy(spec_path, create_spec_path)

        print('Done')
