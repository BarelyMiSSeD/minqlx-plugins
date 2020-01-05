# This is an extension plugin  for minqlx.
# Copyright (C) 2020 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should review a copy of the GNU General Public License
# along with minqlx. See <http://www.gnu.org/licenses/>.

# This is a plugin for the minqlx admin bot.
# It allows the admin to download a map to the server and add it to the server's workshop text file.
# It will them restart the server, if it is empty, so that the map can be played.
# This has worked in my tests every time. I am not guaranteeing it will work in every case.

# Usage Instructions: !getmap <map steam id>
# It will work from RCON with: qlx !getmap <map steam id>

"""
//script cvars to be put in server configuration file (default: server.cfg). Default values shown.
// set the permission level for admins to allow setting and unsetting of the fun warm up mode
set qlx_getmapAdmin "5"
//set the location to the steamcmd.sh containing directory
set qlx_getmapSteamCmd "/home/steam/steamcmd"
"""

import minqlx
import subprocess
import shlex

VERSION = "1.0"


class getmap(minqlx.Plugin):
    def __init__(self):
        self.set_cvar_once("qlx_getmapAdmin", "5")
        self.set_cvar_once("qlx_getmapSteamCmd", "/home/steam/steamcmd")

        self.add_command(("getmap", "get"), self.cmd_getmap, self.get_cvar("qlx_getmapAdmin", int))

    def cmd_getmap(self, player, msg, channel):
        if len(msg) < 2 or not msg[1].isnumeric():
            player.tell("^1You must include a map steam ID number")
        self.download_map(msg[1], player)

    @minqlx.thread
    def download_map(self, map_id, player=None):
        steam_cmd = self.get_cvar("qlx_getmapSteamCmd")
        base_path = self.get_cvar("fs_basepath")

        def run(cmd):
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
            stdout, stderr = proc.communicate()
            return proc.returncode, stdout, stderr

        args = shlex.split("{}/steamcmd.sh +login anonymous +force_install_dir {}/ +workshop_download_item 282440 {}"
                           " +quit".format(steam_cmd, base_path, map_id))
        code, out, err = run(args)
        lines = out.split()
        if player:
            if b'Success.' in lines:
                player.tell("^1Map {} Download Success".format(map_id))
                workshop_file = self.get_cvar("sv_workshopfile")
                f = open("{}/baseq3/{}".format(base_path, workshop_file), "a")
                f.write("{}\n".format(map_id))
                f.close()
                if len(self.players()) == 0:
                    minqlx.console_command("quit")
                else:
                    player.tell("The server is not empty. Restart aborted.")
            else:
                player.tell("^1Map {} download failed.".format(map_id))
