# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# doVote.py is a plugin for minqlx to:
# - allow players to callvote forcing the suggested player switch gotten from !teams
# - Players would "/callvote do" to utilize the vote

# *** IMPORTANT *** This plugin is meant as an add-on to the balance plugin that comes with minqlx
# Do not have the server config load the balance plugin, loading doVote will load balance since
#  this plugin runs as a sub-class of balance. Remove balance from qlx_plugins and add doVote.

# created by BarelyMiSSeD on 8-1-2019

import minqlx
from .balance import balance
import random
import time

VERSION = "1.1"


class doVote(balance):
    def __init__(self):
        super().__init__()
        self.set_cvar_once("qlx_balanceDoVotePerc", "26")
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)
        self.add_command("force_agree", self.cmd_force_agree, 3)
        self.vote_count = [0, 0, 0]

    def handle_vote_called(self, caller, vote, args):
        if vote.lower() == "do":
            if not self.suggested_pair:
                caller.tell("^3There are no suggested players to switch.")
                return minqlx.RET_STOP_ALL
            if not all(self.suggested_agree):
                self.force_switch_vote(caller, vote)
                return minqlx.RET_STOP_ALL

    @minqlx.thread
    def force_switch_vote(self, caller, vote):
        try:
            self.callvote("qlx {}force_agree".format(self.get_cvar("qlx_commandPrefix")),
                          "Force the suggested player switch?")
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called vote /cv {}".format(caller.name, vote))
            voter_perc = self.get_cvar("qlx_balanceDoVotePerc", int)
            if voter_perc > 0:
                self.vote_count[0] = 1
                self.vote_count[1] = 0
                thread_number = random.randrange(0, 10000000)
                self.vote_count[2] = thread_number
                teams = self.teams()
                voters = len(teams["red"]) + len(teams["blue"])
                time.sleep(28.7)
                if self.vote_count[2] == thread_number and self.vote_count[0] / voters * 100 >= voter_perc and\
                        self.vote_count[0] > self.vote_count[1]:
                    self.force_vote(True)
            return
        except Exception as e:
            minqlx.console_print("^1doVote check_force_switch_vote Exception: {}".format(e))

    def cmd_force_agree(self, player=None, msg=None, channel=None):
        if self.suggested_pair:
            self.suggested_agree[0] = True
            self.suggested_agree[1] = True
            if self.game.state in ["in_progress", "countdown"] and not self.in_countdown:
                self.msg("The switch will be executed at the start of next round.")
                return
            # Otherwise, switch right away.
            self.execute_suggestion()
