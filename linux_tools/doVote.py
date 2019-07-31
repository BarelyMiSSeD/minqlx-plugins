
import minqlx
from .balance import balance


class doVote(balance):
    def __init__(self):
        super().__init__()
        self.set_cvar_once("qlx_balanceDoVotePerc", "26")
        self.add_hook("vote_called", self.handle_vote_called)
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
            minqlx.console_print("^1serverBDM check_force_switch_vote Exception: {}".format(e))

    def cmd_force_agree(self, player=None, msg=None, channel=None):
        if self.suggested_pair:
            self.suggested_agree[0] = True
            self.suggested_agree[1] = True
            if self.game.state in ["in_progress", "countdown"] and not self.in_countdown:
                self.msg("The switch will be executed at the start of next round.")
                return
            # Otherwise, switch right away.
            self.execute_suggestion()
