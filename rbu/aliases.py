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


import yaml
import os

from rbu.utils import Constants


class Alias:
    url:str
    dependencies:list[str]


class Aliases:

    _data:dict[Alias]

    def __init__(self):
        with open(os.path.join(Constants.PKGDATADIR, 'aliases.yml'), 'r') as file:
            self._data = {}
            for d in yaml.safe_load(file):
                for name, alias_data in d.items():
                    alias = Alias()
                    
                    if 'url' not in alias_data:
                        raise ValueError(f'Alias {name} has no url')
                    if 'dependencies' not in alias_data:
                        alias_data['dependencies'] = []
                    
                    alias.url = alias_data['url']
                    alias.dependencies = alias_data['dependencies']
                    self._data[name] = alias
                    
    def find_by_url(self, url:str) -> str|None:
        for name, alias in self._data.items():
            if alias.url == url:
                return name
        return None

    def get(self, name:str) -> Alias|None:
        return self._data.get(name)
