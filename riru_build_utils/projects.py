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


import re
import yaml
import os

from riru_build_utils.constants import Constants
from riru_build_utils.utils import print_error


class Project:
    name:str
    api_version:str|None
    url:str
    https_url:str
    ssh_url:str
    depricated:bool
    dependencies:list[str]

class Template:
    name:str
    language:str
    url:str

class Projects:

    _projects_data:dict[str,Project]
    _templates_data:dict[str,dict[str,Template]]

    def __init__(self):
        with open(os.path.join(Constants.PKGDATADIR, 'projects.yml'), 'r') as file:
            self._projects_data = {}
            self._templates_data = {}
            d = yaml.safe_load(file)

            for name, alias_data in d['projects'].items():
                proj = Project()

                if 'name' not in alias_data:
                    print_error(f'Alias {name} has no name')
                if 'https-url' not in alias_data:
                    print_error(f'Alias {name} has no HTTPS url')
                if 'ssh-url' not in alias_data:
                    print_error(f'Alias {name} has no SSH url')
                if 'api-version' not in alias_data:
                    alias_data['api-version'] = None
                if 'dependencies' not in alias_data:
                    alias_data['dependencies'] = []
                if 'depricated' not in alias_data:
                    alias_data['depricated'] = False

                proj.name = alias_data['name']
                proj.api_version = alias_data['api-version']
                proj.url = alias_data['https-url']
                proj.https_url = alias_data['https-url']
                proj.ssh_url = alias_data['ssh-url']
                proj.depricated = alias_data['depricated']
                proj.dependencies = alias_data['dependencies']
                self._projects_data[name] = proj

            for language, language_data in d['templates'].items():
                for name, template_data in language_data.items():
                    template = Template()

                    if 'https-url' not in alias_data:
                        print_error(f'Alias {name} has no HTTPS url')

                    template.name = name
                    template.language = language
                    template.url = template_data['https-url']

                    if language not in self._templates_data:
                        self._templates_data[language] = {}

                    self._templates_data[language][name] = proj

    def find_project_by_url(self, url:str) -> str|None:
        for name, alias in self._projects_data.items():
            if alias.url == url:
                return name
        return None

    def get_project(self, name:str) -> tuple|None:
        ans = self._projects_data.get(name)

        if ans is not None:
            return (name, ans)

        goods:list[Project] = []
        for al in self._projects_data.values():
            if name == al.name:
                goods.append(al)

        if len(goods) == 0:
            return None

        # float for pre-release api version (0.1)
        goods.sort(key=lambda x: float(x.api_version if x.api_version else 0), reverse=True)

        true_name = f'{goods[0].name}' + (f'-{goods[0].api_version}' if goods[0].api_version is not None else '')

        if goods[0].depricated:
            print_error(f'Alias {name} is depricated. There is no point to package it')

        return (true_name, goods[0])

    def get_template(self, language:str, project_type:str) -> Template:
        la = self._templates_data.get(language, None)
        if la is None:
            print_error(f'Language {language} is not supported. Supported: ' + ', '.join(self._templates_data.keys()))

        ans = la.get(project_type)
        if ans is None:
            print_error(f'Template {project_type} is not supported. Supported: ' + ', '.join(self._templates_data[language].keys()))

        return ans
    
    def get_all_projects(self) -> list[Project]:
        return list(self._projects_data.values())
