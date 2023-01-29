# This is an extension plugin  for minqlx.
# Copyright (C) 2023 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# This plugin is meant to be used as an extension to the balance.py included in the minqlx-plugins.
# It will automatically execute a balance at the start of a match.
# It will deny a shuffle vote, if enabled, since it will balance at the start of the match.
# It will give a message that a balance will execute at the start of the game whenever someone calls a shuffle,
#  even when denying shuffle voting is enabled.
# The specqueue plugin is used to ensure we have even teams at game start, so make sure it is loaded before this plugin.
# This plugin will still work without specqueue, but if the total player on the teams add to an odd number, balancing
#  will not occur.

# created by BarelyMiSSeD on 1-28-2023


"""
// Cvar(s)
// Deny a shuffle vote called by a player (1=Deny Vote, 0=Allow Vote).
set qlx_balanceDenyShuffleVote "1"


Commands
toggle : changes the setting of the shuffle vote deny. This does not change the cvar setting,
         so restarting the server will restore it to the setting in the cvar.
"""

import minqlx

VERSION = "1.0"
SUPPORTED_GAMETYPES = ("ad", "ca", "ctf", "dom", "ft", "tdm")


class autobalance(minqlx.Plugin):
    def __init__(self):
        try:
            self.balance = self.plugins["balance"]
        except KeyError:
            raise KeyError("balance.py was not found as a loaded minqlx script.\n"
                           "Check the load order so doVote loads after balance.\n"
                           "Exiting script load.")

        self.set_cvar_once("qlx_balanceDenyShuffleVote", "1")

        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)
        self.add_hook("game_countdown", self.handle_game_countdown)

        self.add_command("toggle", self.toggle_shuffle, 3)

        self.deny_shuffle = bool(int(minqlx.get_cvar("qlx_balanceDenyShuffleVote")))
        try:
            self.specqueue = self.plugins["specqueue"]
        except KeyError:
            self.specqueue = None

    def handle_vote_called(self, caller, vote, args):
        if vote.lower() == "shuffle":
            if self.game.state in ["in_progress", "countdown"]:
                self.msg("^3Game is active. Shuffle vote denied.")
                return minqlx.RET_STOP_ALL
            elif self.deny_shuffle and self.game.type_short in SUPPORTED_GAMETYPES:
                self.msg("^3Shuffle vote ^1denied^3. Teams ^4will be balanced ^3at start of game.")
                return minqlx.RET_STOP_ALL

    @minqlx.delay(1)
    def handle_game_countdown(self):
        teams = self.teams()
        diff = len(teams["red"]) - len(teams["blue"])
        if diff != 0 and self.specqueue:
            self.specqueue.even_the_teams()
        self.center_print("*Balancing Teams*")
        self.msg("^3Balancing by ^2ELO ^3Skill ratings from ^7{}".format(minqlx.get_cvar("qlx_balanceUrl")))
        players = dict([(p.steam_id, self.game.type_short) for p in teams["red"] + teams["blue"]])
        self.balance.add_request(players, self.balance.callback_balance, minqlx.CHAT_CHANNEL)

    def toggle_shuffle(self, player, msg, channel):
        if self.deny_shuffle:
            self.deny_shuffle = False
            player.tell("^3Shuffle vote denying has been ^4Disabled^7. ^3Players may now call shuffle votes.")
        else:
            self.deny_shuffle = True
            player.tell("^3Shuffle vote denying has been ^2Enabled^7. ^3Player's shuffle votes will be denied.")
