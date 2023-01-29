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
# Make sure the balance plugin is loaded prior to loading doVote.

# created by BarelyMiSSeD on 8-1-2019

"""
// sets the percentage of total players on the teams needing to vote yes for it to pass.
// (set to 0 to just pass if yes votes are greater than no votes)
set qlx_balanceDoVotePerc "26"
// enabling this will end the vote at the end of the round (if at least 5 seconds of vote time has passed) and
// pass or fail the vote based on the current votes. (recommend setting above to 0 if this is enabled)
// (0=disabled, 1=enabled)
set qlx_balanceDoVoteEnd "0"
"""

import minqlx
import random
import time

VERSION = "2.0"
SUPPORTED_GAMETYPES = ("ad", "ca", "ctf", "dom", "ft", "tdm")


class doVote(minqlx.Plugin):
    def __init__(self):
        try:
            self.balance = self.plugins["balance"]
        except KeyError:
            raise KeyError("balance.py was not found as a loaded minqlx script.\n"
                           "Check the load order so doVote loads after balance.\n"
                           "Exiting script load.")
        self.set_cvar_once("qlx_balanceDoVotePerc", "26")
        self.set_cvar_once("qlx_balanceDoVoteEnd", "0")
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)
        self.add_hook("vote", self.handle_vote_count)
        self.add_hook("round_end", self.handle_round_end)
        self.add_hook("game_start", self.handle_game_start)
        self.add_command("force_agree", self.cmd_force_agree, 3)
        self.vote_count = [0, 0, 0]
        self.vote_active = False
        self.vote_start_time = None

    def handle_vote_called(self, caller, vote, args):
        if vote.lower() == "do":
            if not self.balance.suggested_pair:
                caller.tell("^3There are no suggested players to switch.")
                return minqlx.RET_STOP_ALL
            if not all(self.balance.suggested_agree):
                self.vote_count = [0, 0, 0]
                self.vote_start_time = time.time()
                self.force_switch_vote(caller, vote)
                return minqlx.RET_STOP_ALL

    def handle_vote_count(self, player, yes):
        if self.vote_count[2]:
            try:
                if yes:
                    self.vote_count[0] += 1
                else:
                    self.vote_count[1] += 1
            except Exception as e:
                minqlx.console_print("^1doVote handle_vote_count Exception: {}".format(e))

    def handle_round_end(self, data):
        self.process_round_end()

    @minqlx.thread
    def process_round_end(self):
        try:
            if self.vote_active and self.get_cvar("qlx_balanceDoVoteEnd", bool) and\
                    time.time() - self.vote_start_time >= 5:
                voter_perc = self.get_cvar("qlx_balanceDoVotePerc", int)
                if voter_perc > 0:
                    teams = self.teams()
                    voters = len(teams["red"]) + len(teams["blue"])
                    if self.vote_count[0] / voters * 100 >= voter_perc and self.vote_count[0] > self.vote_count[1]:
                        time.sleep(1)
                        self.force_vote(True)
                    else:
                        self.force_vote(False)
                else:
                    if self.vote_count[0] > self.vote_count[1]:
                        time.sleep(1)
                        self.force_vote(True)
                    else:
                        self.force_vote(False)
                self.vote_active = False
        except Exception as e:
            minqlx.console_print("^doVote handle_round_end Exception: {}".format(e))

    def handle_game_start(self, data):
        if self.get_cvar("qlx_balanceAuto", bool):
            gt = self.game.type_short
            if gt not in SUPPORTED_GAMETYPES:
                return

            @minqlx.delay(1.5)
            def f():
                players = self.teams()
                players = dict([(p.steam_id, gt) for p in players["red"] + players["blue"]])
                self.balance.add_request(players, self.balance.callback_balance, minqlx.CHAT_CHANNEL)

            f()

    @minqlx.thread
    def force_switch_vote(self, caller, vote):
        try:
            self.callvote("qlx {}force_agree".format(self.get_cvar("qlx_commandPrefix")),
                          "Force the suggested player switch?")
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called vote /cv {}".format(caller.name, vote))
            voter_perc = self.get_cvar("qlx_balanceDoVotePerc", int)
            self.vote_active = True
            self.vote_count[0] = 1
            self.vote_count[1] = 0
            self.vote_count[2] = thread_number = random.randrange(0, 10000000)
            teams = self.teams()
            if voter_perc > 0:
                voters = len(teams["red"]) + len(teams["blue"])
                time.sleep(28.7)
                if self.vote_active and self.vote_count[2] == thread_number and\
                        self.vote_count[0] / voters * 100 >= voter_perc and self.vote_count[0] > self.vote_count[1]:
                    self.force_vote(True)
                    self.vote_active = False
            else:
                time.sleep(28.7)
                if self.vote_active and self.vote_count[2] == thread_number and self.vote_count[0] > self.vote_count[1]:
                    self.force_vote(True)
                    self.vote_active = False
            return
        except Exception as e:
            minqlx.console_print("^1doVote check_force_switch_vote Exception: {}".format(e))

    def cmd_force_agree(self, player=None, msg=None, channel=None):
        if self.balance.suggested_pair:
            self.balance.suggested_agree[0] = True
            self.balance.suggested_agree[1] = True
            if self.game.state in ["in_progress", "countdown"] and not self.balance.in_countdown:
                self.msg("The switch will be executed at the start of next round.")
                return
            # Otherwise, switch right away.
            self.balance.execute_suggestion()
