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
import tempfile

from rbu.aliases import Aliases
from rbu.utils import create_rules


class Tester:
    
    working_dir:str|None
    aliases:Aliases
    
    def __init__(self, working_dir:str|None=None):        
        self.aliases = Aliases()

        self.working_dir = working_dir if working_dir is not None else os.curdir
        
    def test(self, lazy:bool=False):
        test_dir = os.path.join(tempfile.gettempdir(), 'riru-build-utils', 'test')
        os.makedirs(test_dir, exist_ok=True)

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        sisyphus_spec_dir = os.path.join(self.working_dir, 'build-aux', 'sisyphus')
        if not os.path.exists(sisyphus_spec_dir):
            raise Exception(f'No template spec file')

        sisyphus_spec_dir_ls = os.listdir(sisyphus_spec_dir)
        if len(sisyphus_spec_dir_ls) != 1:
            raise Exception(f'No template spec file or too many files in spec dir')
        
        name = sisyphus_spec_dir_ls[0].replace('.spec', '')
        
        if self.aliases.get(name) is None:
            raise Exception(f'Alias \'{name}\' not found')
        
        old_spec_path = os.path.join(test_dir, '.gear', f'{name}.spec')
        template_spec_path = os.path.join(sisyphus_spec_dir, f'{name}.spec')

        gear_path = os.path.join(test_dir, '.gear')
        os.mkdir(gear_path)
        create_rules(self.name, gear_path)
        
        shutil.copytree(self.working_dir, )
