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


import json
import os
import shutil
from subprocess import Popen
import subprocess
import tempfile

from rbu.aliases import Aliases
from rbu.utils import get_project_info, update_spec


class Tester:

    working_dir:str|None
    cleanup:bool
    without_deps:bool
    aliases:Aliases

    def __init__(self, working_dir:str|None=None, cleanup:bool=True, without_deps:bool=False):        
        self.aliases = Aliases()

        self.cleanup = cleanup
        self.working_dir = working_dir if working_dir is not None else os.curdir
        self.without_deps = without_deps

    def test(self):
        os.chdir(self.working_dir)

        sisyphus_spec_dir = os.path.join(self.working_dir, 'build-aux', 'sisyphus')
        if not os.path.exists(sisyphus_spec_dir):
            raise Exception(f'No template spec file')

        sisyphus_spec_dir_ls = os.listdir(sisyphus_spec_dir)
        if len(sisyphus_spec_dir_ls) != 1:
            raise Exception(f'No template spec file or too many files in spec dir')

        name = sisyphus_spec_dir_ls[0].replace('.spec', '')

        test_dir = os.path.join(tempfile.gettempdir(), 'riru-build-utils', 'test', name)
        os.makedirs(test_dir, exist_ok=True)

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        shutil.copytree(self.working_dir, test_dir, ignore=shutil.ignore_patterns('_build'))

        if self.aliases.get(name) is None:
            raise Exception(f'Alias \'{name}\' not found')

        gear_path = os.path.join(test_dir, '.gear')
        os.makedirs(gear_path)
        with open(os.path.join(gear_path, 'rules'), 'w') as file:
            file.write(f'spec: .gear/{name}.spec\n')
            file.write(f'tar: .\n')

        spec_path = os.path.join(gear_path, f'{name}.spec')
        template_spec_path = os.path.join(sisyphus_spec_dir, f'{name}.spec')
        
        project_info = get_project_info()
        version = project_info.get('version')

        update_spec(spec_path, template_spec_path, version)
        Popen(['add_changelog', spec_path, '-e', f'- Test build'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
        
        if self.cleanup:
            Popen(['hsh', '--cleanup-only'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()

        if not self.without_deps:
            for dep in self.aliases.get(name)[1].dependencies:
                dep_dir = os.path.join(tempfile.gettempdir(), 'riru-build-utils', 'test', name + dep)
                url = self.aliases.get(dep)[1].url
                if os.path.exists(dep_dir):
                    shutil.rmtree(dep_dir)
                Popen(['git', 'clone', url, dep_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
                os.chdir(dep_dir)
                Tester(dep_dir, False).test()

        os.chdir(test_dir)
        Popen(['git', 'add', '.'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
        Popen(['gear-hsh', '-v', '--commit', '--no-sisyphus-check=gpg,packager', '--lazy-cleanup']).wait()
