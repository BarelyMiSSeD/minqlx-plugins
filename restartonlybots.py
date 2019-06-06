# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should review a copy of the GNU General Public License
# along with minqlx. See <http://www.gnu.org/licenses/>.

# This is a plugin for the minqlx admin bot.
# It kicks bots out of a server if they are the only ones remaining

"""
// Enable to restart the server when only bots remain. Disabling it will kick all bots when only bots remain.
//   (0=disable, 1=enable)
set qlx_rboRestartServer "0"
"""

import minqlx

VERSION = "1.1"


class restartonlybots(minqlx.Plugin):
    def __init__(self):
        self.set_cvar_once("qlx_rboRestartServer", "0")

        self.add_hook("player_disconnect", self.handle_player_disconnect)

    def handle_player_disconnect(self, player, reason):
        self.check_players()

    @minqlx.delay(5)
    def check_players(self):
        bots_count = 0
        players = self.players()
        for player in players:
            if str(player.steam_id)[0] == "9":
                bots_count += 1

        if bots_count > 0 and bots_count == len(players):
            if self.get_cvar("qlx_rboRestartServer", bool):
                minqlx.console_print("^1Restarting server because no human players are connected.")
                minqlx.console_command("quit")
            else:
                minqlx.console_print("^1Kicking the bots because no human players are connected.")
                for player in players:
                    player.kick()
