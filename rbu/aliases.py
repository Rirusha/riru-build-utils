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

from rbu.utils import Constants


class Alias:
    name:str
    api_version:str|None
    url:str
    dependencies:list[str]


class Aliases:

    _data:dict[str,Alias]

    def __init__(self):
        with open(os.path.join(Constants.PKGDATADIR, 'aliases.yml'), 'r') as file:
            self._data = {}
            for d in yaml.safe_load(file):
                for name, alias_data in d.items():
                    alias = Alias()

                    if 'name' not in alias_data:
                        raise ValueError(f'Alias {name} has no name')
                    if 'url' not in alias_data:
                        raise ValueError(f'Alias {name} has no url')
                    if 'api-version' not in alias_data:
                        alias_data['api-version'] = None
                    if 'dependencies' not in alias_data:
                        alias_data['dependencies'] = []

                    alias.name = alias_data['name']
                    alias.api_version = alias_data['api-version']
                    alias.url = alias_data['url']
                    alias.dependencies = alias_data['dependencies']
                    self._data[name] = alias

    def find_by_url(self, url:str) -> str|None:
        for name, alias in self._data.items():
            if alias.url == url:
                return name
        return None

    def get(self, name:str) -> Alias|None:
        ans = self._data.get(name)

        if ans is not None:
            return ans

        goods:list[Alias] = []
        for al in self._data.values():
            if name == al.name:
                goods.append(al)

        if len(goods) == 0:
            return None

        # float for pre-release api version (0.1)
        goods.sort(key=lambda x: float(x.api_version), reverse=True)
        return self._data[goods[0].string]
