# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should review a copy of the GNU General Public License
# along with minqlx. See <http://www.gnu.org/licenses/>.

# This is a plugin prints the command issuer and the command with arguments to the console
# so they can be seen and logged.
# It gets all the commands loaded on the server automatically.
# Edit the DONT_ECHO list below to exclude the commands you don't want echoed.
# The command !echo will show all the commands being echoed.

import minqlx
import time

DONT_ECHO = ["elo", "elos", "bdm", "bdms", "bdsm", "teams", "teens", "a", "listsounds", "q", "s", "time", "rockets",
             "pummel", "airpummel", "grenades", "plasma", "airrail", "telefrag", "teamtelefrag", "speed"]

VERSION = "1.7"


class echo(minqlx.Plugin):
    def __init__(self):
        self.add_hook("command", self.handle_command, priority=minqlx.PRI_HIGHEST)
        self.add_command("echo", self.cmd_echo)

        self._server_commands = []
        self._command = [None, 0]
        self.populate_server_commands()

    def handle_command(self, caller, command, args):
        self.process_command(caller, command, args)
        return

    def process_command(self, caller, command, args):
        _name = command.name
        _time = time.time()
        if not str(caller).startswith("RconDummyPlayer") and _name in self._server_commands:
            if _name == self._command[0] and _time - self._command[1] < 0.1:
                return
            self._command = [_name, _time]
            minqlx.console_print("^1{} ^3issued command^7: {}".format(caller, args))
        return

    @minqlx.delay(10)
    def populate_server_commands(self):
        loaded_scripts = self.plugins
        for script, handler in loaded_scripts.items():
            try:
                for cmd in handler.commands:
                    self._server_commands.append(cmd.name)
            except:
                continue
        for cmd in DONT_ECHO:
            for entry in self._server_commands:
                if cmd in entry:
                    self._server_commands.remove(entry)

    def cmd_echo(self, player, msg, channel):
        self.list_echo(player)
        return

    @minqlx.thread
    def list_echo(self, player):
        count = 0
        echo_commands = []
        for entry in self._server_commands:
            count += len(entry)
            echo_commands += entry
        player.tell("^2Echoing {} commands^7: ^1{}".format(count, "^7, ^1".join(echo_commands)))
