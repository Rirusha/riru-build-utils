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


import paramiko


class SshWrapper():

    _ssh = paramiko.SSHClient()

    def __init__(self, host:str, username:str):
        self.host = host
        self.username = username
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def execute (self, command) -> list[str]:
        print (f'EXEC:\n\t{self.host.split('.')[0]} {command}')
        self._ssh.connect(
            self.host,
            username=self.username,
            port='222',
            allow_agent=True
        )
        stdin, stdout, stderr = self._ssh.exec_command(command)

        err = stderr.read().decode()
        if err:
            print(err)

        out = stdout.read().decode().split('\n')
        if out:
            print (f'RETURN:\n\t{'\n\t'.join(out)}')
        self._ssh.close ()
        return out
