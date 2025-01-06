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
import random
from subprocess import Popen
import subprocess
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

def update_spec(true_spec_path:str, template_spec_path:str, version:str):
    changelog = ['%changelog\n']
    template_spec = []
    
    if os.path.exists(true_spec_path):
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
            elif line.startswith('%define api_version') and '@LAST_API_VERSION@' in line:
                file.write(line.replace('@LAST_API_VERSION@', cut_version(version)[0]))
            elif line.startswith('%define minor_version') and '@LAST_MINOR_VERSION@' in line:
                file.write(line.replace('@LAST_MINOR_VERSION@', cut_version(version)[1]))
            elif line.startswith('Release:'):
                file.write('Release: alt1')
            else:
                file.write(line)

            file.write('\n')

        file.write('\n')
        file.writelines(changelog)

def print_on_no():
    print(random.choice([
        '>:(',
        'Ok...',
        'nah, whatever...',
    ]))

def create_spec(orig_spec_path:str):
    if not os.path.exists('_build'):
        Popen(['meson', 'setup', '_build'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()

    project_info_json = Popen(['meson', 'introspect', '--projectinfo', '_build'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).communicate()[0]

    project_info = json.loads(project_info_json)
    name = project_info.get('descriptive_name', '')
    license_ = project_info.get('license', ['GPL-3.0-or-later'])[0]
    dependencies = []

    meson_path = os.path.join(os.path.curdir, 'meson.build')
    with open(meson_path, 'r') as file:
        for line in file.readlines():
            if 'dependency(' in line:
                dependencies.append(line.split('dependency(')[1].strip().strip('()').split(',')[0].strip('\''))

    print ()
    print('Data:')
    print('Name: ' + name)
    print('License: ' + license_)
    print('Dependencies: ' + ('-' if len(dependencies) == 0 else ', '.join(dependencies)))
    print ()

    if not ask('All is chiky-pooky?'):
        print_on_no()
        return
    
    spec_dir_path = os.path.join(os.path.curdir, 'build-aux', 'sisyphus')
    if not os.path.exists(spec_dir_path):
        os.makedirs(spec_dir_path)

    new_spec_path = os.path.join(spec_dir_path, f'{name}.spec')
    
    if os.path.exists(new_spec_path):
        print(f'Spec file \'{new_spec_path}\' already exists.')
        if not ask('Overwrite?'):
            print_on_no()
            return

        os.remove(new_spec_path)

    with open(orig_spec_path, 'r') as file:
        with open(new_spec_path, 'w') as new_file:
            for line in file.readlines():
                # Stupid is my second name
                new_file.write(line.replace('@NAME@', name).replace('@LICENSE@', license_).replace('@DEPENDENCIES@', '\n'.join(map(lambda x: f'BuildRequires: pkgconfig({x})', dependencies))))

def cut_version(version:str) -> tuple[str]:
    api_version = ''
    minor_version = ''

    version_parts = version.split('.')
    if len(version_parts) == 1:
        raise ValueError('Version must be in the format 0.x.y or x.y')
    elif len(version_parts) == 2:
        if version_parts[0] == '0':
            raise ValueError('Version must be in the format 0.x.y or x.y or x.y.z')

        api_version = version_parts[0]
        minor_version = version_parts[1]
    elif len(version_parts) == 3:
        if version_parts[0] == '0':
            api_version = version_parts[0] + '.' + version_parts[1]
            minor_version = version_parts[2]
        else:
            api_version = version_parts[0]
            minor_version = version_parts[1] + '.' + version_parts[2]
    else:
        raise ValueError('Version must be in the format 0.x.y or x.y or x.y.z')

    if api_version == '' or minor_version == '':
        raise ValueError(f'Strange version \'{version}\'')
    
    return (api_version, minor_version)
