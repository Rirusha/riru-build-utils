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


import requests
from rbu.ssh_wrapper import SshWrapper


GYLE = SshWrapper('gyle.altlinux.org', 'alt_rirusha')
GITERY = SshWrapper('gitery.altlinux.org', 'alt_rirusha')

class Constants:
    PKGDATADIR = ''

def ask(question: str) -> bool:
    i = input(question + ' [Y/n] ').lower()
    
    if i == 'y':
        return True
    elif i == 'n':
        return False
    else:
        return True

def get_package_repo_version(name:str) -> str|None:
    resp = requests.get(f'https://rdb.altlinux.org/api/package/package_info?name={name}&branch=sisyphus')
    if resp.status_code == 404:
        return None

    return resp.json()['packages'][0]['version']
