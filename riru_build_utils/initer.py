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
import uuid
from riru_build_utils.projects import Project, Projects
from riru_build_utils.utils import ask


class Initer:

    clone_path:str|None
    language:str
    project_type:str
    name:str
    projects:Projects

    def __init__(self, language:str, project_type:str, name:str):
        self.projects = Projects()

        self.language = language
        self.project_type = project_type
        self.name = name
        self.clone_path = os.path.join(os.curdir, name)

    def init(self):
        template = self.projects.get_template(self.language, self.project_type)

        if os.path.exists(self.clone_path):
            if self.skip_exists:
                return

            if ask('Path exists. Delete?'):
                shutil.rmtree (self.clone_path)

        Popen(['git', 'clone', template.url, self.clone_path]).wait()
        shutil.rmtree(os.path.join(self.clone_path, '.git'))
