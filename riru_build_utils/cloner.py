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
from subprocess import Popen
from riru_build_utils.projects import Project, Projects
from riru_build_utils.utils import ask


class Cloner:

    names:list[str]|None
    projects:Projects
    all_:bool
    skip_exists:bool

    def __init__(self, names:list[str]|None, all_:bool=False, skip_exists:bool=False):
        self.projects = Projects()

        self.names = names
        self.all_ = all_
        self.skip_exists = skip_exists

    def clone(self):
        if self.names is not None:
            for name in self.names:
                clone_path = os.path.join(os.curdir, name)

                proj:Project
                if self.projects.get_project(name) is None:
                    print(f'Project {name} not found')
                    return

            for name in self.names:
                clone_path = os.path.join(os.curdir, name)

                proj:Project
                _, proj = self.projects.get_project(name)

                if os.path.exists(clone_path):
                    if self.skip_exists:
                        print(f'Skip {name}...')
                        continue

                    if ask(f'Path {clone_path} exists. Remove?'):
                        shutil.rmtree (clone_path)
                        
                Popen(['git', 'clone', proj.url, clone_path]).wait()

        elif self.all_:
            Cloner(list(map(lambda x: x.name, filter(lambda x: not x.depricated, self.projects.get_all_projects()))), False, True).clone()

        else:
            print('Nothing to do')
