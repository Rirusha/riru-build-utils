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

def create_rules(name:str, path:str):
    with open(os.path.join(path, 'rules'), 'w') as file:
        file.write(f'spec: .gear/{name}.spec\n')
        file.write(f'tar: {name}\n')

def update_spec (true_spec_path:str, template_spec_path:str, version:str):
    changelog = ['%changelog\n']
    template_spec = []
    
    with open(true_spec_path, 'r') as file:
        is_changelog = False
        
        for line in file.readlines():
            if line.startswith('%changelog'):
                is_changelog = True
            else:
                if is_changelog:
                    changelog.append(line);
        
    with open(template_spec_path, 'r') as file:
        for line in file.readlines():
            if line.startswith('%changelog'):
                break
            
            template_spec.append(line.strip())
        
    with open(true_spec_path, 'w') as file:
        for line in template_spec:
            if line.startswith('Version:') and '@LAST@' in line:
                file.write(line.replace('@LAST@', version))
            elif line.startswith('Release:'):
                file.write('Release: alt1')
            else:
                file.write(line)

            file.write('\n')

        file.writelines(changelog)
