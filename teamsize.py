# teamsize.py is a plugin for minqlx to:
# -limit the teamsize admins are able to set when using !teamsize or !ts
# created by BarelyMiSSeD on 7-12-2019
#
"""
//Set these cvar(s) in your server.cfg (or wherever you set your minqlx variables).:
set qlx_teamsizemin "2"
set qlx_teamsizemax "12"
"""

import minqlx

VERSION = "v1.00"


class teamsize(minqlx.Plugin):
    def __init__(self):
        self.add_command(("teamsize", "ts"), self.cmd_teamsize, priority=minqlx.PRI_HIGH)

        # Cvar(s).
        self.set_cvar_once("qlx_teamsizemin", "2")
        self.set_cvar_once("qlx_teamsizemax", "12")

    def cmd_teamsize(self, player, msg, channel):
        if len(msg) < 2:
            return
        try:
            n = int(msg[1])
        except ValueError:
            return
        if n > self.get_cvar("qlx_teamsizemax", int):
            player.tell("^6That teamsize is too large")
            return minqlx.RET_STOP_ALL
        elif n < self.get_cvar("qlx_teamsizemin", int):
            player.tell("^6That teamsize is too small")
            return minqlx.RET_STOP_ALL
