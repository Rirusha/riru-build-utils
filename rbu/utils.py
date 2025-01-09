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
import re
from subprocess import Popen
import subprocess
import requests
from rbu.aliases import Aliases
from rbu.ssh_wrapper import SshWrapper
from rbu.appstream_python import AppstreamComponent


GYLE = SshWrapper('gyle.altlinux.org', 'alt_rirusha')
GITERY = SshWrapper('gitery.altlinux.org', 'alt_rirusha')


class Dependency:
    name:str
    version:str|None
    
    def __str__(self):
        return self.name


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
    
def find_appstream_file() -> str|None:
    data_path = os.path.join(os.path.curdir, 'data')
    
    if os.path.exists(data_path):
        for file in os.listdir(data_path):
            if '.appdata.xml' in file or '.metainfo.xml' in file:
                return os.path.join(data_path, file)

    return None

def find_meson_var(name:str, meson_path:str) -> str|None:
    with open(meson_path, 'r') as file:
            for line in file.readlines():
                if line.startswith(f'{name} = '):
                    return line.split(f'{name} = ')[1].strip().strip('\'')

    return None

def create_spec(orig_spec_path:str):
    if not os.path.exists('_build'):
        Popen(['meson', 'setup', '_build'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()

    project_info_json = Popen(['meson', 'introspect', '--projectinfo', '_build'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).communicate()[0]

    project_info = json.loads(project_info_json)
    name:str = project_info.get('descriptive_name', '')
    license_ = project_info.get('license', ['GPL-3.0-or-later'])[0]
    dependencies:list[Dependency] = []

    aliases = Aliases()
    true_name, alias = aliases.get(name)
    url = alias.url
    
    appstream_path =find_appstream_file()
    if appstream_path:
        appstream = AppstreamComponent()
        appstream.load_file(find_appstream_file())
        
        app_id = appstream.id
        summary = appstream.summary.get_default_text()
        description = appstream.description.to_plain_text()
        description = re.sub(r' *\n ', ' ', description)
        description = re.sub(r' +', ' ', description)
        description = description.replace('•', '-')
    else:
        app_id = 'ASSERT'
        summary = 'ASSERT'
        description = '%summary.'
        
    meson_path = os.path.join(os.path.curdir, 'meson.build')
    with open(meson_path, 'r') as file:
        for line in file.readlines():
            # TODO: Realize multistring dependency
            if 'dependency(' in line:
                dep_string = line
                dep_name = dep_string.split('dependency(')[1].strip().strip('()').split(',')[0].strip('\'')
                if dep_name == 'threads':
                    continue
                
                version = None
                if 'version:' in dep_string:
                    version_string = dep_string.split('version:')[1].strip().strip('()').split(',')[0].strip('\'')
                    if not re.match(r'[=><]+ [\d\.]+', version_string):
                        v = find_meson_var(version_string)
                        if v:
                            version = v
                    else:
                        version = version_string

                dependency = Dependency()
                dependency.name = dep_name
                dependency.version = version
                dependencies.append(dependency)

    if app_id == '@APP_ID@':
        app_id = find_meson_var('app_id', meson_path)
        
        if not app_id:
            app_id = 'ASSERT'
            
    if name.startswith('lib'):
        gir_name = kebab2pascal(name.replace('lib', '', 1))
    else:
        gir_name = 'ASSERT'

    print ()
    print('Data:')
    print('App ID: ' + app_id)
    print('Name: ' + name)
    print('Gear Name: ' + gir_name)
    print('Summary: ' + summary)
    print('Description: ' + ' '.join(description.split('\n')))
    print('License: ' + license_)
    print('Dependencies: ' + ('-' if len(dependencies) == 0 else ', '.join(map(lambda x: f'{x.name} {x.version}', dependencies))))
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
                new_line = line

                new_line = new_line.replace('@APP_ID@', app_id)
                new_line = new_line.replace('@NAME@', name)
                new_line = new_line.replace('@GIR_NAME@', gir_name)
                new_line = new_line.replace('@SUMMARY@', summary)
                new_line = new_line.replace('@DESCRIPTION@', format_description(description))
                new_line = new_line.replace('@URL@', url)
                new_line = new_line.replace('@LICENSE@', license_)
                new_line = new_line.replace('@BUILD_DEPENDENCIES@', '\n'.join(map(lambda x: f'BuildRequires: pkgconfig({x.name}){f' {x.version}' if x.version else ''}', dependencies)))

                new_file.write(new_line)

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

def format_description(description:str) -> str:
    # https://www.altlinux.org/Spec#%25description
    MAX_SIZE = 72
    
    new_desc:list[str] = []
    for line in description.split('\n'):
        new_desc_line = ''

        lines_splitted = line.split(' ')
        for line_splitted in lines_splitted:
            if len(new_desc_line) + len(line_splitted) <= MAX_SIZE:
                new_desc_line += line_splitted + ' '
            else:
                new_desc.append(new_desc_line.strip())
                new_desc_line = line_splitted + ' '

        new_desc.append(new_desc_line.strip())

    return '\n'.join(new_desc)

def kebab2pascal(kebab:str) -> str:
    return ''.join(map(lambda x: x.capitalize(), kebab.split('-')))
