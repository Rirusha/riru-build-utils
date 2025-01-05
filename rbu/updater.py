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


import shutil
import subprocess
import sys
import tarfile
import tempfile
from subprocess import Popen
import os

import requests
from rbu.aliases import Alias, Aliases
from rbu.utils import GITERY, GYLE, ask, get_package_repo_version, print_on_no, update_spec


class Updater:
    
    url:str
    name:str
    version:str|None
    tag:str|None
    root_task:str|None
    test:bool
    alias:Alias
    
    def __init__(self, name:str, tag:str|None, root_task:str|None, test:bool):
        aliases = Aliases()
        
        nname = name
        name = name.lower()

        if name.endswith('.git') or name.startswith('https://'):
            nname = name
            
            if not name.endswith('.git'):
                name += '.git'
            
            name = aliases.find_by_url(name)
            
            if name is None:
                raise Exception(f'Alias for \'{nname}\' not found')
            
        self.alias = aliases.get(name)
            
        if self.alias is None:
            raise Exception(f'Alias \'{name}\' not found')

        self.url = self.alias.url
        self.name = name
        self.tag = tag
        self.root_task = root_task
        self.test = test

    def update(self):
        root_tpm = os.path.join(tempfile.gettempdir(), 'riru-build-utils')
        wd = os.path.join(root_tpm, self.name)
        os.makedirs(wd, exist_ok=True)
        os.chdir(wd)
        
        if self.tag is None:
            if os.path.exists(self.name):
                shutil.rmtree(self.name)

            print(f'Cloning \'{self.name}\' repository...')
            Popen(['git', 'clone', self.url, self.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            os.chdir(self.name)

            output = Popen(['git', 'describe', '--tags', '--abbrev=0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).communicate()[0]
            self.tag = output.split('\n')[0]
            
        if self.tag is None or self.tag == '':
            raise Exception(f'Tag for \'{self.name}\' not found')

        self.version = self.tag.replace('v', '') if self.tag is not None else None
        repo_version = get_package_repo_version(self.name)

        if repo_version is not None:
            if repo_version >= self.version:
                print(f'Newer or equal version of \'{self.name}\' found in repository: {repo_version}')
                print('Skipping...')
                return

        print ()
        print('Data:')
        print('Url: ' + self.url)
        print('Name: ' + self.name)
        print('Version: ' + self.version)
        print('Tag: ' + self.tag)
        print('HasRootTask: ' + ('true' if self.root_task is not None else 'false'))
        print('Test: ' + ('true' if self.test else 'false'))
        print ()
        
        if not ask('All is chiky-pooky?'):
            print_on_no()
            return

        os.chdir(wd)
        
        archive_url = ''
        sources_name = ''
        if self.url.startswith('https://github.com/'):
            archive_url = self.url.replace('.git', '') + f'/archive/refs/tags/{self.tag}.tar.gz'
            sources_name = self.alias.name + '-' + self.version
        elif self.url.startswith('https://gitlab.gnome.org/'):
            archive_url = self.url.replace('.git', '') + f'/-/archive/{self.tag}/{self.alias.name}-{self.tag}.tar.gz'
            sources_name = self.alias.name + '-' + self.tag
        else:
            raise Exception(f'Unknown repository type: {self.url}')

        resp = requests.get(archive_url)
        resp.raise_for_status()
        
        archive_file = os.path.join(wd, self.name + '.tar.gz')
        with open(archive_file, 'wb') as file:
            file.write(resp.content)

        sources_dir = os.path.join(wd, sources_name)
        if os.path.exists(sources_dir):
            shutil.rmtree(sources_dir)

        with tarfile.open(archive_file, 'r:gz') as tar:
            tar.extractall(wd)

        all_alt_git = GITERY.execute('ls packages')[1:]
        
        found = False
        for line in all_alt_git:
            if line.split(' ')[-1].replace('.git', '') == self.name:
                found = True
                break

        gitery_path = os.path.join(wd, self.name + '-alt')

        if os.path.exists(gitery_path):
            shutil.rmtree(gitery_path)

        if not found:
            GITERY.execute(f'init-db {self.name}')
            Popen(['git', 'clone', f'gitery:packages/{self.name}.git', gitery_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            if os.path.exists(os.path.join(gitery_path, self.name)):
                shutil.rmtree(os.path.join(gitery_path, self.name))
            shutil.copytree(sources_dir, os.path.join(gitery_path, self.name))
            os.chdir(gitery_path)
            Popen(['git', 'add', '.'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['git', 'commit', '-m', 'Add upstream sources'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['git', 'push'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
        else:
            Popen(['git', 'clone', f'gitery:packages/{self.name}.git', gitery_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            shutil.rmtree(os.path.join(gitery_path, self.name))
            shutil.copytree(sources_dir, os.path.join(gitery_path, self.name))
            os.chdir(gitery_path)
            
        gear_path = os.path.join(gitery_path, '.gear')
        if not os.path.exists(gear_path):
            os.mkdir(gear_path)
            with open(os.path.join(gear_path, 'rules'), 'w') as file:
                file.write(f'spec: .gear/{self.alias.name}.spec\n')
                file.write(f'tar: {self.name}\n')
            
            Popen(['git', 'add', '.'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['git', 'commit', '-m', 'Add rules file'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['git', 'push'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()

        old_spec_path = os.path.join(gitery_path, '.gear', f'{self.alias.name}.spec')
        template_spec_path = os.path.join(wd, sources_dir, 'build-aux', 'sisyphus', f'{self.alias.name}.spec')

        if not os.path.exists(template_spec_path):
            raise Exception(f'No template spec file in \'{self.name}\' {self.tag}')

        spec_file_created = not os.path.exists(old_spec_path)

        update_spec(old_spec_path, template_spec_path, self.version)
        
        if spec_file_created:
            Popen(['add_changelog', old_spec_path, '-e', f'- Initial build for sisyphus'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['git', 'add', old_spec_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['git', 'commit', '-m', 'Add spec file'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['git', 'push'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['git', 'tag', '-a', '-s', '-m', f'{self.name} {self.version}-alt1', f'{self.version}-alt1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
        else:
            Popen(['add_changelog', old_spec_path, '-e', f'- New version: {self.version}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['git', 'add', '.'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['gear-commit', '--no-edit'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['git', 'push'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
            Popen(['gear-create-tag'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()

        Popen(['git', 'push', '--tags'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()

        task_id = self.root_task if self.root_task is not None else GYLE.execute('task new')[0]

        for dep in self.alias.dependencies:
            Updater(dep, None, task_id).update()

        try:
            GYLE.execute(f'task add {task_id} repo {self.name} {self.version}-alt1')
        except Exception as e:
            print ('Somethig went wrong, abort task...')
            GYLE.execute(f'task rm {task_id}')
            sys.exit(1)

        if self.root_task is None:
            GYLE.execute(f'task run {task_id}{' --commit' if not self.test else ''}')
            print (f'Done: \'{self.name}\' with task id: {task_id}')
        else:
            print (f'Done: \'{self.name}\'')
