# This is an extension plugin  for minqlx.
# Copyright (C) 2020 BarelyMiSSeD (github)
# https://github.com/BarelyMiSSeD/minqlx-plugins

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# highping.py is a plugin for minqlx to:
# - check players when they join a team for a ping that is higher than the setting.
# - Put the players back to spec who do not meet the ping requirements
# - allow admins to execute the high ping  check on all players using the !999 command

# created by BarelyMiSSeD on 3-16-2020

"""
// sets the ping limit looked for when getting a players average ping
set qlx_highpingMax "250"
// sets the number of ping samples taken for each player checked
// Adjust this lower/higher if the ping test results are taking too long or are inaccurate
set qlx_highpingSamples "10"
"""

import minqlx
import time

VERSION = "1.1"


class highping(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.set_cvar_once("qlx_highpingMax", "250")
        self.set_cvar_once("qlx_highpingSamples", "10")
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_command("999", self.cmd_check_pings, 5)

    def handle_team_switch(self, player, old_team, new_team):
        self.check_ping(player, new_team)

    @minqlx.thread
    def check_ping(self, player, new_team):
        if new_team != "spectator":
            ping = 0
            samples = self.get_cvar("qlx_highpingSamples", int)
            for x in range(samples):
                ping += player.ping
                time.sleep(0.2)
            ping = ping / samples
            if ping >= self.get_cvar("qlx_highpingMax", int):
                player.put("spectator")
                player.tell("^1Your ping is too high to play on this server, as a result you were put to spectate.")

    def cmd_check_pings(self, player=None, msg=None, channel=None):
        self.check_pings()

    @minqlx.thread
    def check_pings(self):
        players = self.teams()
        teams = players['red'] + players['blue'] + players['free']
        pings = {}
        max_ping = self.get_cvar("qlx_highpingMax", int)
        samples = self.get_cvar("qlx_highpingSamples", int)
        for player in teams:
            pings[player] = 0
            for x in range(samples):
                pings[player] += player.ping
                time.sleep(0.2)
            pings[player] = pings[player] / samples

        for player, ping in pings:
            if ping >= max_ping:
                player.put("spectator")
                player.tell("^1Your ping is too high to play on this server, as a result you were put to spectate.")
