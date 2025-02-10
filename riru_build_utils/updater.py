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
import shutil
import subprocess
import sys
import tarfile
import tempfile
from subprocess import Popen
import os

# import requests
from riru_build_utils.projects import Project, Projects
from riru_build_utils.appstream_python.Component import AppstreamComponent
from riru_build_utils.tester import Tester
from riru_build_utils.utils import GITERY, GYLE, ask, find_appstream_file, get_package_repo_version, print_error, print_on_no, update_spec


class Updater:

    url:str
    name:str
    version:str|None
    tag:str|None
    root_task:str|None
    for_test:bool
    with_test:bool
    alias:Project

    def __init__(self, name:str|None, tag:str|None, root_task:str|None, for_test:bool, with_test:bool):
        aliases = Projects()

        if not name:
            spec_dir = os.path.join(os.curdir, 'build-aux', 'sisyphus')

            if os.path.exists(spec_dir):
                if len(os.listdir(spec_dir)) == 1:
                    spec_name = os.listdir(spec_dir)[0]
                    name = spec_name.replace('.spec', '')
                else:
                    print_error('No spec found or too many files found in spec dir')
            else:
                print_error('No spec dir found')

        nname = name
        name = name.lower()

        if name.endswith('.git') or name.startswith('https://'):
            nname = name

            if not name.endswith('.git'):
                name += '.git'

            name = aliases.find_project_by_url(name)

            if name is None:
                print_error(f'Alias for \'{nname}\' not found')

        name, self.alias = aliases.get_project(name)

        if self.alias is None:
            print_error(f'Alias \'{name}\' not found')

        self.url = self.alias.url
        self.name = name
        self.tag = tag
        self.root_task = root_task
        self.for_test = for_test
        self.with_test = with_test

    def update(self):
        if self.with_test:
            Tester().test()
        
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
            print_error(f'Tag for \'{self.name}\' not found')

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
        print('Test: ' + ('true' if self.for_test else 'false'))
        print ()

        if not ask('All is chiky-pooky?'):
            print_on_no()
            return

        os.chdir(wd)

        # archive_url = ''
        # sources_name = ''
        # if self.url.startswith('https://github.com/'):
        #     archive_url = self.url.replace('.git', '') + f'/archive/refs/tags/{self.tag}.tar.gz'
        #     sources_name = self.alias.name + '-' + self.version
        # elif self.url.startswith('https://gitlab.gnome.org/'):
        #     archive_url = self.url.replace('.git', '') + f'/-/archive/{self.tag}/{self.alias.name}-{self.tag}.tar.gz'
        #     sources_name = self.alias.name + '-' + self.tag
        # else:
        #     print_error(f'Unknown repository type: {self.url}')

        # resp = requests.get(archive_url)
        # resp.raise_for_status()

        # archive_file = os.path.join(wd, self.name + '.tar.gz')
        # with open(archive_file, 'wb') as file:
        #     file.write(resp.content)

        # sources_dir = os.path.join(wd, sources_name)
        # if os.path.exists(sources_dir):
        #     shutil.rmtree(sources_dir)

        # with tarfile.open(archive_file, 'r:gz') as tar:
        #     tar.extractall(wd)

        gitery_path = os.path.join(wd, self.name + '-alt')
        # gitery_src_path = os.path.join(gitery_path, self.name)
        old_spec_path = os.path.join(gitery_path, '.gear', f'{self.name}.spec')
        template_spec_path = os.path.join(wd, 'template.spec')

        # if not os.path.exists(template_spec_path):
        #     print_error(f'No template spec file in \'{self.name}\' {self.tag}')
        # if not os.path.exists(sources_dir):
        #     print_error(f'No sources dir at \'{sources_dir}\'')

        if os.path.exists(gitery_path):
            shutil.rmtree(gitery_path)

        all_alt_git = GITERY.execute('ls packages')[1:]

        found = False
        for line in all_alt_git:
            if line.split(' ')[-1].replace('.git', '') == self.name:
                found = True
                break

        if not found:
            GITERY.execute(f'init-db {self.name}')

        Popen(['git', 'clone', f'gitery:packages/{self.name}.git', gitery_path], text=True).wait()
        # if os.path.exists(gitery_src_path):
        #     shutil.rmtree(gitery_src_path)
        # shutil.copytree(sources_dir, os.path.join(gitery_path, self.name))
        os.chdir(gitery_path)
        
        gear_path = os.path.join(gitery_path, '.gear')
        if not os.path.exists(gear_path):
            os.makedirs(gear_path)

        rules_path = os.path.join(gear_path, 'rules')
        if not found:
            with open(rules_path, 'w') as file:
                file.write(f'spec: .gear/{self.name}.spec\n')
                file.write(f'tar: v@version@:.\n')
                file.write(f'diff: v@version@:. . exclude=.gear/** name=@name@-@version@-alt.patch\n')
                
            Popen(['git', 'add', '.'], text=True).wait()
            Popen(['git', 'commit', '-m', 'Init with rules file'], text=True).wait()
            Popen(['git', 'push'], text=True).wait()

            Popen(['git', 'remote', 'add', '--tags', 'upstream', self.url], text=True).wait()
            Popen(['gear-remotes-save', 'upstream'], text=True).wait()
            Popen(['gear-remotes-fetch'], text=True).wait()

            Popen(['git', 'add', '.'], text=True).wait()
            Popen(['git', 'commit', '-m', 'Add upstream remote'], text=True).wait()
            Popen(['git', 'push'], text=True).wait()
        else:
            Popen(['gear-remotes-restore'], text=True).wait()
            Popen(['gear-remotes-fetch'], text=True).wait()
            
        Popen(['git', 'merge', '--no-edit', '-X', 'theirs', self.tag, '--allow-unrelated-histories'], text=True).wait()
            
        template_spec_content = Popen(['git', 'show', f'upstream/main:build-aux/sisyphus/{self.alias.name.lower()}.spec'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).communicate()[0]
        
        with open(template_spec_path, 'w') as file:
            file.write(template_spec_content)

        spec_file_created_now = not os.path.exists(old_spec_path)

        update_spec(old_spec_path, template_spec_path, self.version)
        
        Popen(['gear-store-tags', '-ac'], text=True).wait()

        if spec_file_created_now:
            Popen(['add_changelog', old_spec_path, '-e', f'- Initial build.'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()
        else:
            changelog:list[str] = [f'- New version: {self.version}']

            appstream_path =find_appstream_file(gitery_path)
            if appstream_path:
                appstream = AppstreamComponent()
                appstream.load_file(appstream_path)

                release = appstream.releases.pop()
                if release.version == self.version:
                    description = release.description.to_plain_text().strip()
                    description = re.sub(r' *\n ', ' ', description)
                    description = re.sub(r' +', ' ', description)
                    description = description.replace('•', '*')
                    changelog.extend(map(lambda x: f'- {x}' if not x.startswith('x') else x, description.split('\n')))

                    print('Changelog:')
                    for line in changelog:
                        print(line)
                    if not ask('All is chiky-pooky?'):
                        print_on_no()
                        return

            Popen(['add_changelog', old_spec_path, '-e', '.\n'.join(changelog)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).wait()

        Popen(['git', 'add', '.'], text=True).wait()
        Popen(['gear-commit', '--no-edit'], text=True).wait()
        Popen(['git', 'push'], text=True).wait()
        Popen(['gear-create-tag'], text=True).wait()

        Popen(['git', 'push', 'origin', f'{self.version}-alt1'], text=True).wait()

        os.chdir(wd)

        task_id = self.root_task if self.root_task is not None else GYLE.execute('task new')[0]

        for dep in self.alias.dependencies:
            Updater(dep, None, task_id, self.for_test).update()

        try:
            GYLE.execute(f'task add {task_id} repo {self.name} {self.version}-alt1')
        except Exception as e:
            print ('Somethig went wrong, abort task...')
            GYLE.execute(f'task rm {task_id}')
            sys.exit(1)

        if self.root_task is None:
            GYLE.execute(f'task run {task_id}{' --commit' if not self.for_test else ''}')
            print (f'Done: \'{self.name}\' with task id: {task_id}')
        else:
            print (f'Done: \'{self.name}\'')
