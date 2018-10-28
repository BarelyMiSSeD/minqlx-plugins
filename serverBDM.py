# serverBDM.py is a plugin for minqlx to:
# - Calculate and store players Basic Damage Metric (BDM) on the server.
# - It is a server side skill calculation similar to ELO.
# - Since it is server side your BDM is based only on performance on each individual server.

# created by BarelyMiSSeD on 5-5-2018
#
"""
# **** If you want to enable the !teams and !balance commands ise the balance.py from
# https://github.com/BarelyMiSSeD/minqlx-plugins/blob/master/balance.py or the commands will conflict.
"""
"""
**** CVARs ****
// Minqlx Bot Permission level needed to perform admin functions
set qlx_bdmAdmin "3"
// The default BDM rating given to new players
set qlx_bdmDefaultBDM "1222"
// The minimum BDM rating (if calculated BDM falls below this, this value will be set)
set qlx_bdmMinRating "300"
// The maximum BDM rating (if calculated BDM goes above this, this value will be set)
set qlx_bdmMaxRating "3000"
// Balance with BDM Ratings at the start of a team game
//   This will disable shuffle vote calling
set qlx_bdmBalanceAtGameStart "0"
// balance the teams based on BDM after a shuffle vote passes
set qlx_bdmBalanceAfterShuffleVote "0"
// Balance teams if the teams are not even
set qlx_bdmBalanceUnevenTeams "0"
// Minimum team BDM Average Difference before a player switch is suggested
set qlx_bdmMinimumSuggestionDiff", "60")
// Print the BDM change results to the server console at the completion of BDM calculations
set qlx_bdmConsolePrintBdmChange "1"
// Enable the player switch that is gotten from !bteams
//   This feature is so the !bteams function can be seen by players but not enabled
//   until the server admin decides enough stats have been collected
set qlx_bdmEnableSwitch "0"
// Set BDM to respond to the !teams bot command, if this is not enabled the !teams command will reset
//  any suggested switch made from the !bteams command
set qlx_bdmRespondToTeamsCommand "0"
// Set BDM to respond to the !balance bot command
set qlx_bdmRespondToBalanceCommand "0"
// Set to "1" to enable '/callvote do' on the server to allow voting to force the suggested switch from !bteams
set qlx_bdmEnableDoVote "1"
// Set to "1" to display a message on player join to show games played and rating status to the server
set qlx_bdmPrintJoinMsg "1"
// If it is set to different than "0" it will use that number as a percentage of players who are playing
//  that are needed to vote on the '/cv do' vote for the script to pass the vote if at least that percentage
//  vote and more vote yes than no.
set qlx_bdmPlayerPercForVote "26"  // set to "0" to disable
// This enables/disables the use of the ELO_URL to set initial player bdm. ( 0 = off, 1 = on )
set qlx_bdmSetIntitialBDM "1"
// These are used to calculate the initial bdm of a player who has not been on the server yet.
//  The ELO_URL will be queried to get the players elo for the game type and the formula bdm=m*elo+b is used
//   to calculate the initial bdm. Adjust the values if needed to get the desired initial bdm.
set qlx_bdmMCalculation "0.92"
set qlx_bdmBCalculation "-250"
// The BDM Player join message can be modified with the following cvar. The formatting instructions are:
//    The cvar is the structure of the join message. You have the ability to put any of the following information into
//    the join message (the numbers in front of the information will be used in the message format).
// 0: player name
// 1: bdm rating
// 2: bdm games completed on the server
// 3: bdm games left
// 4: all bdm games played (completed + left)
// 5: bdm games quit percentage
// 6: games played on the server
// 7: all games completed on the server (completed + left)
// 8: all games left on the server
// 9: all games quit percentage
// The default message format is shown in the set command below. The numbers in between the curly brackets dictate
//   which field of information to insert into that place. The curly brackets with the numbers get replaced with the
//   information for the player beside that number's description. An example of changing the default to only show
//   the player's name, BDM rating, all BDM games played, BDM games quit, BDM quit percentage could look something like
//   "^6{0}^7: BDM rating^3{1} ^7BDM games played ^4{2}^7, games quit: ^1{3} ^7(^6{5}^7％)"
// Setting the cvar to that would use the information listed above next to the numbers 0, 3, 4, 5, and 9 and it would
//   print the join message out with the curly brackets and the number in between with the information for that player.
// The carrat and number (example: ^1) is the Quake Live color code that colors the text.
// You can make your own join message, just make sure to put the correct number for the player's information you
//   desire in between curly brackets and in the correct location in your line of text.
// *** Note: Quake Live will put your join message onto multiple lines if it is too long. ***
set "qlx_bdmJoinMessage" "^6{0}^7: ^3{6} ^7games here ^2{2} ^4BDM ^7games ^7(quit ^6{5}^7％) ^7rating: ^2{1}^7."


// *** Clan Arena Settings ***
set qlx_bdmCaKillPts "50"
// *** Capture the Flag Settings ***
set qlx_bdmCtfKillPts "50"
set qlx_bdmCtfCapPts "300"
set qlx_bdmCtfAssistPts "150"
set qlx_bdmCtfDefensePts "50"
// *** Instagib Capture the Flag Settings ***
set qlx_bdmICtfKillPts "25"
set qlx_bdmICtfCapPts "500"
set qlx_bdmICtfAssistPts "150"
set qlx_bdmICtfDefensePts "100"
// *** Freeze Tag Settings ***
set qlx_bdmFtKillPts "100"
set qlx_bdmFtThawPts "100"
set qlx_bdmFtFrozenPts "50"
// *** Team Death Match Settings ***
set qlx_bdmTdmKillPts "75"
set qlx_bdmTdmDeathPts "25"
// *** Free For All Settings ***
set qlx_bdmFfaKillPts "500"
// *** General Calculations Settings ***
set qlx_bdmDamageRcvdPerc "1"
// Minimum Round Time percentage needed for players stats to be counted/calculated
set qlx_bdmMinTimePerc "60"
// Minimum Rounds (in round based games) needed for players stats to be counted/calculated
set qlx_bdmMinRounds "5"
// Minimum players that have played enough of the match needed for players stats to be counted/calculated
set qlx_bdmMinimumTeamSize "3"

"""

import minqlx
import time
from threading import Lock
import random
import requests

VERSION = "1.04.00"
# TO_BE_ADDED = ("duel")
BDM_GAMETYPES = ("ft", "ca", "ctf", "ffa", "ictf", "tdm")
TEAM_BASED_GAMETYPES = ("ca", "ctf", "ft", "ictf", "tdm")
ROUND_BASED_GAMETYPES = ("ca", "ft")
BDM_KEY = "minqlx:players:{}:bdm:{}:{}"
ELO_URL = "qlstats.net"


class serverBDM(minqlx.Plugin):
    def __init__(self):
        # cvars
        self.set_cvar_once("qlx_bdmAdmin", "3")
        self.set_cvar_once("qlx_bdmDefaultBDM", "1222")
        self.set_cvar_once("qlx_bdmMinRating", "300")
        self.set_cvar_once("qlx_bdmMaxRating", "3000")
        self.set_cvar_once("qlx_bdmBalanceAtGameStart", "0")
        self.set_cvar_once("qlx_bdmBalanceAfterShuffleVote", "0")
        self.set_cvar_once("qlx_bdmMinimumSuggestionDiff", "60")
        self.set_cvar_once("qlx_bdmBalanceUnevenTeams", "0")
        self.set_cvar_once("qlx_bdmConsolePrintBdmChange", "1")
        self.set_cvar_once("qlx_bdmEnableSwitch", "0")
        self.set_cvar_once("qlx_bdmRespondToTeamsCommand", "0")
        self.set_cvar_once("qlx_bdmRespondToBalanceCommand", "0")
        self.set_cvar_once("qlx_bdmEnableDoVote", "1")
        self.set_cvar_once("qlx_bdmPrintJoinMsg", "1")
        self.set_cvar_once("qlx_bdmPrintBdmStatsEveryMap", "0")
        self.set_cvar_once("qlx_bdmPlayerPercForVote", "26")
        self.set_cvar_once("qlx_bdmSetIntitialBDM", "1")
        self.set_cvar_once("qlx_bdmMCalculation", "0.92")
        self.set_cvar_once("qlx_bdmBCalculation", "-250")
        self.set_cvar_once("qlx_bdmJoinMessage",
                           "^6{0}^7: ^3{6} ^7games here ^2{2} ^4BDM ^7games ^7(quit ^6{5}^7％) ^7rating: ^2{1}^7.")
        # CA
        self.set_cvar_once("qlx_bdmCaKillPts", "50")
        # CTF
        self.set_cvar_once("qlx_bdmCtfKillPts", "50")
        self.set_cvar_once("qlx_bdmCtfCapPts", "300")
        self.set_cvar_once("qlx_bdmCtfAssistPts", "150")
        self.set_cvar_once("qlx_bdmCtfDefensePts", "50")
        # ICTF
        self.set_cvar_once("qlx_bdmICtfKillPts", "25")
        self.set_cvar_once("qlx_bdmICtfCapPts", "500")
        self.set_cvar_once("qlx_bdmICtfAssistPts", "150")
        self.set_cvar_once("qlx_bdmICtfDefensePts", "100")
        # FT
        self.set_cvar_once("qlx_bdmFtKillPts", "100")
        self.set_cvar_once("qlx_bdmFtThawPts", "100")
        self.set_cvar_once("qlx_bdmFtFrozenPts", "50")
        # TDM
        self.set_cvar_once("qlx_bdmTdmKillPts", "75")
        self.set_cvar_once("qlx_bdmTdmDeathPts", "25")
        # FFA
        self.set_cvar_once("qlx_bdmFfaKillPts", "500")
        # GLOBAL
        self.set_cvar_once("qlx_bdmDamageRcvdPerc", "1")
        self.set_cvar_once("qlx_bdmMinTimePerc", "60")
        self.set_cvar_once("qlx_bdmMinRounds", "5")
        self.set_cvar_once("qlx_bdmMinimumTeamSize", "3")

        # Minqlx bot Hooks
        self.add_hook("chat", self.handle_chat)
        self.add_hook("stats", self.handle_stats)
        self.add_hook("player_connect", self.handle_player_connect)
        self.add_hook("player_loaded", self.handle_player_loaded, priority=minqlx.PRI_LOWEST)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("round_countdown", self.handle_round_countdown)
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)
        self.add_hook("vote", self.handle_vote_count)
        self.add_hook("vote_ended", self.handle_vote_ended)
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("round_end", self.handle_round_end)
        self.add_hook("game_start", self.handle_game_start)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("map", self.handle_map)

        # Minqlx bot commands
        self.add_command(("bdmversion", "bdmv"), self.cmd_bdmversion)
        self.add_command("bdm", self.bdm_cmd)
        self.add_command(("bdmh", "bdmhistory"), self.bdm_history)
        self.add_command(("bdms", "bdsm"), self.bdms_cmd)
        self.add_command("bteams", self.bteams_cmd)
        self.add_command(("teams", "teens"), self.teams_cmd)
        self.add_command("balance", self.balance_cmd, self.get_cvar("qlx_bdmAdmin", int))
        self.add_command("a", self.cmd_bdmagree)
        self.add_command("do", self.cmd_bdmdo, self.get_cvar("qlx_bdmAdmin", int))
        self.add_command("setbdm", self.cmd_set_bdm, self.get_cvar("qlx_bdmAdmin", int))
        self.add_command("bbalance", self.cmd_bdmbalance, self.get_cvar("qlx_bdmAdmin", int))
        self.add_command("damage", self.cmd_damage_status)
        self.add_command("dmg", self.cmd_dmg_status)
        self.add_command("gamestatus", self.cmd_game_status, self.get_cvar("qlx_bdmAdmin", int))
        self.add_command("mark_agree", self.cmd_mark_agree, self.get_cvar("qlx_bdmAdmin", int))

        # Script Variables, Lists, and Dictionaries
        self.lock = Lock()
        self._bdm_gtype = self.game.type_short
        self._played_time = {}
        self._disconnected_players = {}
        self._team_switchers = {}
        self._spectating_players = {}
        self._save_previous_bdm = {}
        self._match_stats = {}
        self._player_stats = {}
        self._record_events = {}
        self._agreeing_players = None
        self._players_agree = [False, False]
        self._suggested_switch = 0
        self.in_countdown = False
        self.game_active = False
        self.rounds_played = 0
        self.game_start = 0
        self.player_count = 0
        self.player_join_rating_displayed = []
        self.vote_count = [0, 0, 0]

        self.create_db()
        if self.game.state == "in_progress":
            self.players_in_teams()

    # ==============================================
    #               Event Handler's
    # ==============================================
    def handle_chat(self, player, msg, channel):
        # don't process the chat if it was in the wrong channel
        if channel == "chat":
            if "what is bdm" in msg.lower():
                self.msg("^6BDM ^7is ^6B^7asic ^6D^7amage ^6M^7etric. It is a server side skill calculation similar to "
                         "^5ELO^7. Since it is server side your ^6BDM ^7is based only on performance on each "
                         "individual server.\nCommands: ^1{0}bdm^7, ^1{0}bdms^7, ^1{0}bdmh"
                         .format(self.get_cvar("qlx_commandPrefix")))
            return

    def handle_stats(self, stats):
        if self.game.state != "in_progress":
            return
        if self._bdm_gtype == "ctf" and stats["TYPE"] == "PLAYER_MEDAL":
            self.record_ctf_events(stats["DATA"]["STEAM_ID"], stats["DATA"]["MEDAL"])
        elif self._bdm_gtype == "ft":
            self.record_ft_events(stats)

    def handle_player_connect(self, player):
        sid = str(player.steam_id)
        if sid[0] == "9":
            return
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self._bdm_gtype
        self.set_bdm_field(player, game_type, "rating", self.get_cvar("qlx_bdmDefaultBDM"), False)
        self.set_bdm_field(player, game_type, "games_completed", "0", False)
        self.set_bdm_field(player, game_type, "games_left", "0", False)
        if self.get_cvar("qlx_bdmSetIntitialBDM", bool) and self.get_bdm_field(player, game_type, "games_completed") +\
                self.get_bdm_field(player, game_type, "games_left") == 0:
            self.set_initial_bdm(player, game_type)

    def handle_player_loaded(self, player):
        sid = str(player.steam_id)
        if sid[0] == "9":
            return
        if not self.get_cvar("qlx_bdmPrintBdmStatsEveryMap", bool):
            if sid in self.player_join_rating_displayed:
                return
            else:
                self.player_join_rating_displayed.append(sid)
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self._bdm_gtype
        if self.get_cvar("qlx_bdmPrintJoinMsg", bool) and str(player.steam_id)[0] != "9":
            try:
                games_completed = self.get_db_field(player, "minqlx:players:{}:games_completed")
            except Exception as e:
                games_completed = 0
                minqlx.console_print("Games Completed retrieval error: {}".format(e))
            try:
                games_left = self.get_db_field(player, "minqlx:players:{}:games_left")
            except Exception as e:
                games_left = 0
                minqlx.console_print("Games Left retrieval error: {}".format(e))
            try:
                if games_completed > 0:
                    quit_percentage = round((games_left / games_completed) * 100)
                else:
                    quit_percentage = 0
            except Exception as e:
                quit_percentage = 0
                minqlx.console_print("Games Quit Percentage calculation error: {}".format(e))
            games_played = games_completed + games_left
            try:
                bdm_rating = self.get_bdm_field(player, game_type, "rating")
            except Exception as e:
                bdm_rating = self.get_cvar("qlx_bdmDefaultBDM", int)
                minqlx.console_print("BDM Rating retrieval error: {}".format(e))
            try:
                bdm_completed = self.get_bdm_field(player, game_type, "games_completed")
            except Exception as e:
                bdm_completed = 0
                minqlx.console_print("BDM Completed retrieval error: {}".format(e))
            try:
                bdm_left = self.get_bdm_field(player, game_type, "games_left")
            except Exception as e:
                bdm_left = 0
                minqlx.console_print("BDM Left retrieval error: {}".format(e))
            bdm_total = bdm_completed + bdm_left
            try:
                bdm_quit_percentage = round(bdm_left / bdm_completed * 100)
            except Exception as e:
                bdm_quit_percentage = 0
                minqlx.console_print("Quit calculation error: {}".format(e))
            join_msg = self.get_cvar("qlx_bdmJoinMessage").replace("%", "％")
            self.msg(join_msg.format(player, bdm_rating, bdm_completed, bdm_left, bdm_total, bdm_quit_percentage,
                                     games_played, games_completed, games_left, quit_percentage))

    def handle_player_disconnect(self, player, reason):
        self.player_disconnect_record([player, player.stats])
        try:
            self.player_join_rating_displayed.remove(str(player.steam_id))
        except ValueError:
            pass

    def handle_team_switch(self, player, old_team, new_team):
        self.team_switch_record(player, new_team, old_team)
        if self._suggested_switch == 1:
            self._suggested_switch = -1

    def handle_round_countdown(self, number):
        self.in_countdown = True
        if all(self._players_agree):
            # If we don't delay the switch a bit, the round countdown sound and
            # text disappears for some weird reason.
            @minqlx.next_frame
            def f():
                self.execute_switch()
            f()

    def handle_round_start(self, number):
        self.in_countdown = False
        if not self.game_active:
            self.rounds_played = 0
            self.game_active = True

    def handle_round_end(self, data):
        self.rounds_played = int(data["ROUND"])
        if self._bdm_gtype in ROUND_BASED_GAMETYPES:
            self.round_stats_record()
        if self._bdm_gtype in TEAM_BASED_GAMETYPES:
            minqlx.console_print("^1RED^7: ^7{} ^6::: ^4BLUE^7: {}".format(self.game.red_score, self.game.blue_score))

    def handle_game_start(self, data):
        self.game_start = int(round(time.time() * 1000))

        # Give a little time for the game to insert everyone into a team
        @minqlx.next_frame
        def set_up():
            self.players_in_teams()
        set_up()

        if self.get_cvar("qlx_bdmBalanceAtGameStart", bool) and self.get_cvar("qlx_bdmEnableSwitch", bool):
            self.msg("^2Balancing ^1Teams ^7based on ^6BDM ^7stats.")
            self.cmd_bdmbalance()

    def handle_game_end(self, data):
        if data["ABORTED"]:
            self.reset_data()
            return
        self.process_game()

    def handle_vote_called(self, caller, vote, args):
        minqlx.console_print("{} ^7called vote: ^6{} {}".format(caller, vote, args))
        if vote.lower() == "bbalance" or\
                vote.lower() == "balance" and self.get_cvar("qlx_bdmRespondToBalanceCommand", bool):
            self.callvote("qlx {}bbalance".format(self.get_cvar("qlx_commandPrefix")),
                          "Balance Teams based on database stored BDMs?")
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called vote /cv {}".format(caller.name, vote))
            return minqlx.RET_STOP_ALL
        elif vote.lower() == "shuffle" and self._bdm_gtype in BDM_GAMETYPES:
            if self.get_cvar("qlx_bdmBalanceAtGameStart", bool) and self.get_cvar("qlx_bdmEnableSwitch", bool):
                self.msg("^3Shuffle vote denied. Teams ^4will be balanced ^3at start of game.")
                return minqlx.RET_STOP_ALL
        elif vote.lower() == "do" and self.get_cvar("qlx_bdmEnableDoVote", bool):
            if not self._agreeing_players:
                caller.tell("^3There are no suggested players to switch.")
                return minqlx.RET_STOP_ALL
            self.check_force_switch_vote(caller, vote)
            return minqlx.RET_STOP_ALL

    def handle_vote_count(self, player, yes):
        if yes:
            self.vote_count[0] += 1
        else:
            self.vote_count[1] += 1

    def handle_vote_ended(self, votes, vote, args, passed):
        self.vote_count[2] = 0
        if passed and vote.lower() == "shuffle" and self.get_cvar("qlx_bdmBalanceAfterShuffleVote", bool):
            if self._bdm_gtype not in TEAM_BASED_GAMETYPES:
                return

            @minqlx.delay(2.5)
            def b():
                self.msg("^3Shuffle ^7vote called, ^2Balancing ^1Teams ^7based on ^6BDM ^7stats.")
                self.cmd_bdmbalance()

            b()

    def handle_map(self, mapname, factory):
        self._bdm_gtype = self.game.type_short
        self.create_db()
        self.reset_data()

    # ==============================================
    #               Minqlx Bot Commands
    # ==============================================
    def cmd_set_bdm(self, player, msg, channel):
        if self._bdm_gtype not in BDM_GAMETYPES:
            player.tell("^7This is not a supported BDM game type.")
            return minqlx.RET_STOP_ALL
        if len(msg) < 3:
            player.tell("^7Usage: <player id> <rating>")
            return minqlx.RET_STOP_ALL
        try:
            pid = int(msg[1])
            rating = int(msg[2])
        except ValueError:
            player.tell("^1Invalid player ID or RATING.")
            return minqlx.RET_STOP_ALL
        if pid < 0 or pid > 63:
            player.tell("^1Invalid player ID")
            return minqlx.RET_STOP_ALL
        target_player = self.player(pid)
        if not target_player:
            player.tell("^1There is no player using that player ID.")
            return minqlx.RET_STOP_ALL
        if rating > self.get_cvar("qlx_bdmMaxRating", int) or rating < self.get_cvar("qlx_bdmMinRating", int):
            player.tell("^1Unreasonable player RATING.")
            return minqlx.RET_STOP_ALL
        sid = str(target_player.steam_id)
        if sid[0] == "9":
            player.tell("^1Setting a BOT's BDM is not allowed.")
            return
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self._bdm_gtype
        self.set_bdm_field(target_player, game_type, "rating", rating)
        player.tell("^4Rating^7: The player {} ^7has been set to a ^4bdm ^7rating of ^1{}^7 for game type {}."
                    .format(target_player, rating, game_type))
        player.tell("^7The rating will be adjusted from this point as games are recorded.")

    def bdm_cmd(self, player, msg, channel):
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self._bdm_gtype
        if game_type in BDM_GAMETYPES:
            if len(msg) > 1:
                try:
                    pid = int(msg[1])
                    player = self.player(pid)
                except minqlx.NonexistentPlayerError:
                    player.tell("Invalid client ID.")
                    return
                except ValueError:
                    player.tell("^3Use a valid player ID.")
                    return minqlx.RET_STOP_ALL

            if self.check_entry_exists(player, game_type, "rating"):
                rating = self.get_bdm_field(player, game_type, "rating")
                completed = self.get_bdm_field(player, game_type, "games_completed")
                left = self.get_bdm_field(player, game_type, "games_left")
                games_here = left + completed
                channel.reply("^7The ^3{} ^6bdm ^7for {} ^7is ^2{} ^7(games here: ^6{}^7)"
                              .format(game_type.upper(), player, rating, games_here))
            else:
                channel.reply("^7There is no stored ^3{} ^bdm for {}^7. A rating of ^6{} ^7will be used."
                              .format(game_type.upper(), player, self.get_cvar("qlx_bdmDefaultBDM", int)))

    def bdm_history(self, player, msg, channel):
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self._bdm_gtype
        if game_type in BDM_GAMETYPES:
            if len(msg) > 1:
                try:
                    pid = int(msg[1])
                    player = self.player(pid)
                except minqlx.NonexistentPlayerError:
                    player.tell("Invalid client ID.")
                    return
                except ValueError:
                    player.tell("^3Use a valid player ID.")
                    return minqlx.RET_STOP_ALL

            if self.check_entry_exists(player, game_type, "rating"):
                rating = self.get_bdm_field(player, game_type, "rating")
                completed = self.get_bdm_field(player, game_type, "games_completed")
                left = self.get_bdm_field(player, game_type, "games_left")
                games_here = left + completed
                if games_here > 0:
                    quit_perc = float(left) / float(games_here) * 100
                else:
                    quit_perc = 0
                channel.reply("^7The ^3{0} ^6bdm ^7for {1} ^7is ^2{2} ^7(games here: ^6{3} ^7Quit: ^6{4:.1f}％)"
                              .format(game_type.upper(), player, rating, games_here, quit_perc))
                history_msg = []
                for x in range(1, 6, 1):
                    if self.check_entry_exists(player, game_type, "rating{}".format(x)):
                        history_rating = self.get_bdm_field(player, game_type, "rating{}".format(x))
                        history_msg.append("^{}{}".format(x, history_rating))
                if len(history_msg) > 0:
                    channel.reply("^6BDM History for {}: {}".format(player, ", ".join(history_msg)))
                else:
                    channel.reply("There is no BDM history for {}".format(player))
            else:
                channel.reply("^7There is no stored ^3{} ^bdm for {}^7. A rating of ^6{} ^7will be used."
                              .format(self._bdm_gtype.upper(), player, self.get_cvar("qlx_bdmDefaultBDM", int)))

    @minqlx.thread
    def bdms_cmd(self, player, msg, channel):
        if self._bdm_gtype in BDM_GAMETYPES:
            if self.get_cvar("g_factory").lower() == "ictf":
                game_type = "ictf"
            else:
                game_type = self._bdm_gtype
            teams = self.teams()
            clients = len(teams["red"])
            if clients:
                t_dict = {}
                r_msg = []
                for p in teams["red"]:
                    t_dict[str(p)] = self.get_bdm_field(p, game_type, "rating")
                r_dict = sorted(((v, k) for k, v in t_dict.items()), reverse=True)
                for k, v in r_dict:
                    r_msg.append("^7{}^7:^1{}^7".format(v, k))
                self.msg(", ".join(r_msg))

            clients = len(teams["blue"])
            if clients:
                t_dict = {}
                b_msg = []
                for p in teams["blue"]:
                    t_dict[str(p)] = self.get_bdm_field(p, game_type, "rating")
                b_dict = sorted(((v, k) for k, v in t_dict.items()), reverse=True)
                for k, v in b_dict:
                    b_msg.append("^7{}^7:^4{}^7".format(v, k))
                self.msg(", ".join(b_msg))

            clients = len(teams["free"])
            if clients:
                t_dict = {}
                f_msg = []
                for p in teams["free"]:
                    t_dict[str(p)] = self.get_bdm_field(p, game_type, "rating")
                f_dict = sorted(((v, k) for k, v in t_dict.items()), reverse=True)
                for k, v in f_dict:
                    f_msg.append("^7{}^7:^2{}^7".format(v, k))
                self.msg(", ".join(f_msg))

            clients = len(teams["spectator"])
            if clients:
                t_dict = {}
                s_msg = []
                for p in teams["spectator"]:
                    t_dict[str(p)] = self.get_bdm_field(p, game_type, "rating")
                s_dict = sorted(((v, k) for k, v in t_dict.items()), reverse=True)
                for k, v in s_dict:
                    s_msg.append("^7{}^7:^3{}^7".format(v, k))
                self.msg(", ".join(s_msg))

        else:
            self.msg("^7The current ^2{} ^7game type does not have player bdm ratings.".format(self._bdm_gtype))

    def teams_cmd(self, player, msg, channel):
        if self.get_cvar("qlx_bdmRespondToTeamsCommand", bool):
            self.bteams_cmd(player, msg, channel)
        else:
            self._agreeing_players = None
            self._players_agree = [False, False]

    def balance_cmd(self, player, msg, channel):
        if self.get_cvar("qlx_bdmRespondToBalanceCommand", bool):
            self.cmd_bdmbalance(player, msg, channel)

    @minqlx.thread
    def bteams_cmd(self, player, msg, channel):
        if self._bdm_gtype in TEAM_BASED_GAMETYPES:
            if self.get_cvar("g_factory").lower() == "ictf":
                game_type = "ictf"
            else:
                game_type = self._bdm_gtype
            teams = self.teams()
            red_clients = len(teams["red"])
            blue_clients = len(teams["blue"])
            red_team_bdm = {}
            blue_team_bdm = {}
            red_bdm = 0
            blue_bdm = 0
            if red_clients == 0 and blue_clients == 0:
                self.msg("^3The teams are empty of players.")
                return
            elif red_clients != blue_clients:
                self.msg("^3Both teams should have the same number of players.")
                return

            for client in teams["red"]:
                rating = self.get_bdm_field(client, game_type, "rating")
                red_bdm += int(rating)
                red_team_bdm[str(client.steam_id)] = int(rating)
            red_bdm /= red_clients

            for client in teams["blue"]:
                rating = self.get_bdm_field(client, game_type, "rating")
                blue_bdm += int(rating)
                blue_team_bdm[str(client.steam_id)] = int(rating)
            blue_bdm /= blue_clients

            message = ["^7Team Balance: ^1{} ^7vs. ^4{}".format(round(red_bdm), round(blue_bdm))]
            difference = round(red_bdm) - round(blue_bdm)
            if difference > 0:
                message.append(" ^7- Difference: ^1{}".format(difference))
            elif difference < 0:
                message.append(" ^7- Difference: ^4{}".format(abs(difference)))
            else:
                message.append(" ^7- ^2EVEN")
            self.msg("".join(message))

            min_suggestion = self.get_cvar("qlx_bdmMinimumSuggestionDiff", int)
            if abs(difference) >= min_suggestion:
                diff = 99999
                new_difference = 99999
                players = [None, None]
                for r in red_team_bdm:
                    for b in blue_team_bdm:
                        temp_r = red_team_bdm.copy()
                        temp_b = blue_team_bdm.copy()
                        temp_r[b] = temp_b[b]
                        temp_b[r] = temp_r[r]
                        del temp_r[r]
                        del temp_b[b]
                        avg_r = 0
                        for p in temp_r:
                            avg_r += temp_r[p]
                        avg_r /= red_clients
                        avg_b = 0
                        for p in temp_b:
                            avg_b += temp_b[p]
                        avg_b /= blue_clients
                        if abs(avg_r - avg_b) < diff:
                            new_difference = round(avg_r - avg_b)
                            diff = abs(avg_r - avg_b)
                            players = (r, b)

                if abs(new_difference) < abs(difference) and abs(difference) >= min_suggestion:
                    if not self._agreeing_players or self._agreeing_players[0] != players[0] or\
                            self._agreeing_players[1] != players[1]:
                        self._agreeing_players = (players[0], players[1])
                        self._players_agree = [False, False]
                    self._suggested_switch = 1
                    self.msg("^6Switch ^1::^7{}^1::^7<-> ^4::^7{}^4:: ^6{}a ^7to agree."
                             .format(self.player(int(players[0])), self.player(int(players[1])),
                                     self.get_cvar("qlx_commandPrefix")))
                else:
                    self.msg("^6Teams look good.")
                    self._agreeing_players = None
                    self._players_agree = [False, False]
                    self._suggested_switch = 0
            else:
                self.msg("^6Teams look good.")
                self._agreeing_players = None
                self._players_agree = [False, False]
                self._suggested_switch = 0
        else:
            self.msg("^7This game type is not a supported Team-Based BDM game type.")
            self._suggested_switch = 0

    def cmd_mark_agree(self, player, msg, channel):
        self._players_agree[0] = True
        self._players_agree[1] = True
        if self.game.state == "in_progress" and not self.in_countdown:
            self.msg("^3The players will be switched at the start of next round.")
            return
        # Otherwise, switch right away.
        self.execute_switch()

    def cmd_bdmagree(self, player, msg, channel):
        if self._suggested_switch == -1:
            self.msg("^6Team makeups have changed. Run ^1{0}{1} ^6again."
                     .format(self.get_cvar("qlx_commandPrefix"),
                             "teams" if self.get_cvar("qlx_bdmRespondToTeamsCommand", bool) else "bteams"))
            self.clear_suggestion()
            return
        """After the bot suggests a switch, players in question can use this to agree to the switch."""
        if self._agreeing_players and not all(self._players_agree):
            player1 = self.player(int(self._agreeing_players[0]))
            player2 = self.player(int(self._agreeing_players[1]))
            if player1 == player:
                self._players_agree[0] = True
                if not self._players_agree[1]:
                    self.msg("^3Player ^6{} ^2agrees ^7with the switch.".format(player1))
            elif player2 == player:
                self._players_agree[1] = True
                if not self._players_agree[0]:
                    self.msg("^3Player ^6{} ^2agrees ^7with the switch.".format(player2))
            if all(self._players_agree):
                # If the game's in progress and we're not in the round countdown, wait for next round.
                if self.game.state == "in_progress" and not self.in_countdown:
                    self.msg("^3The players will be switched at the start of next round.")
                    return
                # Otherwise, switch right away.
                self.execute_switch()
            else:
                if not self._players_agree[0] and not self._players_agree[1]:
                    self.msg("^3Player ^6{} ^7and ^6{} ^7still need to ^2agree ^7to the switch."
                             .format(player1, player2))
                elif not self._players_agree[0]:
                    self.msg("^3Player ^6{} ^7still needs to ^2agree ^7to the switch.".format(player1))
                else:
                    self.msg("^3Player ^6{} ^7still needs to ^2agree ^7to the switch.".format(player2))

    def cmd_bdmversion(self, player, msg, channel):
        channel.reply("^7This server is running serverBDM.py ^2{0} version {1} by BarelyMiSSeD\n"
                      "https://github.com/BarelyMiSSeD/minqlx-plugins".format(self.__class__.__name__, VERSION))

    def cmd_bdmdo(self, player, msg, channel):
        """Forces a suggested switch to be done."""
        minqlx.console_print("Status: {} {}".format(self._suggested_switch, self._agreeing_players))
        if self._agreeing_players and self._suggested_switch == 1:
            self.execute_switch()
        elif len(msg) > 1:
            if self._agreeing_players and self._suggested_switch == -1 and msg[1] == "force":
                self.execute_switch()
            else:
                player.tell("^6Use ^1{}do force ^6to execute the switch even though team makeup has changed."
                            .format(self.get_cvar("qlx_commandPrefix")))
        elif self._agreeing_players and self._suggested_switch == -1:
            player.tell("^6Use ^1{}do force ^6to execute the switch even though team makeup has changed."
                        .format(self.get_cvar("qlx_commandPrefix")))

    @minqlx.delay(1)
    def cmd_bdmbalance(self, player=None, msg=None, channel=None):
        if self._bdm_gtype in TEAM_BASED_GAMETYPES and self._bdm_gtype not in BDM_GAMETYPES:
            self.msg("^3This is not a team based game type with bdm ratings.")
            return
        elif self._bdm_gtype not in TEAM_BASED_GAMETYPES:
            self.msg("^3This is not a game type supported by this balance function.")
            return
        teams = self.teams().copy()
        if len(teams["red"] + teams["blue"]) < 4:
            self.msg("^3There are not enough players on the teams to perform a balance.")
            return
        exclude = None
        avg_red = 0
        avg_blue = 0
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self._bdm_gtype
        if len(teams["red"] + teams["blue"]) % 2 != 0:
            if self.get_cvar("qlx_bdmBalanceUnevenTeams", bool):
                if "specqueue" in minqlx.Plugin._loaded_plugins:
                    exclude = minqlx.Plugin._loaded_plugins["specqueue"]\
                        .return_spec_player((teams["red"] + teams["blue"]))[0]
                else:
                    lowest = self.get_cvar("qlx_bdmMaxRating", int)
                    for player in teams["red"] + teams["blue"]:
                        bdm = self.get_bdm_field(player, game_type, "rating")
                        if bdm < lowest:
                            lowest = bdm
                            exclude = player
                if exclude:
                    if exclude in teams["red"]:
                        teams["red"].remove(exclude)
                    elif exclude in teams["blue"]:
                        teams["blue"].remove(exclude)
            else:
                self.msg("^3The teams are not even. Balancing can't occur.")
                return
        # Start out by evening out the number of players on each team.
        diff = len(teams["red"]) - len(teams["blue"])
        if abs(diff) > 1:
            if diff > 0:
                for i in range(diff - 1):
                    player = teams["red"].pop()
                    player.put("blue")
                    teams["blue"].append(player)
            elif diff < 0:
                for i in range(abs(diff) - 1):
                    player = teams["blue"].pop()
                    player.put("red")
                    teams["red"].append(player)
        # Start shuffling by looping through our suggestion function until
        # there are no more switches that can be done to improve teams.
        switch = self.suggest_switch(teams)
        if switch:
            while switch:
                player1 = switch[0]
                player2 = switch[1]
                self.switch(player1, player2)
                teams["blue"].append(player1)
                teams["red"].append(player2)
                teams["blue"].remove(player2)
                teams["red"].remove(player1)
                switch = self.suggest_switch(teams)
            avg_red = self.team_average(teams["red"])
            avg_blue = self.team_average(teams["blue"])
            message = ["^7Team Balance: ^1{} ^7vs. ^4{}".format(round(avg_red), round(avg_blue))]
            difference = round(avg_red - avg_blue)
            if difference > 0:
                message.append(" ^7- Difference: ^1{}".format(difference))
            elif difference < 0:
                message.append(" ^7- Difference: ^4{}".format(abs(difference)))
            else:
                message.append(" ^7- ^2EVEN")
            self.msg("".join(message))
        else:
            self.msg("^4Teams look good^1! ^7Nothing to balance.")
        if exclude:
            if avg_blue > avg_red:
                exclude.put("red")
            else:
                exclude.put("blue")
            self.msg("^6{} ^4was not included in the balance.".format(exclude))

    @minqlx.thread
    def cmd_damage_status(self, player=None, msg=None, channel=None):
        teams = self.teams()
        if len(teams["red"] + teams["blue"] + teams["free"] + teams["spectator"]) == 0:
            self.msg("^3No players connected")
        if self.game.state not in ["in_progress", "countdown"]:
            self.msg("^3Match is not in progress")
        self.msg("^6ID ^5Player ^3Kills^7/^3Deaths^7: ^3Damage Dealt^7/^3Received^7:")
        if self._bdm_gtype in TEAM_BASED_GAMETYPES:
            red_team = []
            blue_team = []
            for player in teams["red"]:
                red_team.append("^1{} ^6{} ^2{}^7/^1{} ^2{}^7/^1{}"
                                .format(player.id, player,
                                        player.stats.kills, player.stats.deaths, player.stats.damage_dealt,
                                        player.stats.damage_taken))
            for player in red_team:
                self.msg(player)
            for player in teams["blue"]:
                blue_team.append("^4{} ^6{} ^2{}^7/^1{} ^2{}^7/^1{}"
                                 .format(player.id, player,
                                         player.stats.kills, player.stats.deaths, player.stats.damage_dealt,
                                         player.stats.damage_taken))
            for player in blue_team:
                self.msg(player)
        else:
            for player in teams["free"]:
                self.msg("^2{} ^6{} ^2{}^7/^1{} ^2{}^7/^1{}"
                         .format(player.id, player,
                                 player.stats.kills, player.stats.deaths, player.stats.damage_dealt,
                                 player.stats.damage_taken))

    def cmd_dmg_status(self, player=None, msg=None, channel=None):
        teams = self.teams()
        if self.game.state not in ["in_progress", "countdown"]:
            self.msg("^3Match is not in progress")
        if len(msg) > 1:
            try:
                pid = int(msg[1])
                player = self.player(pid)
            except minqlx.NonexistentPlayerError:
                self.msg("^1Invalid player ID.")
                return
            except ValueError:
                self.msg("^3Use a valid player ID.")
                return
        if player in teams["spectator"]:
            self.msg("^3{} ^3is spectating".format(player))
            return
        if self._bdm_gtype in TEAM_BASED_GAMETYPES:
            if player in teams["red"]:
                self.msg("^1{} ^6{} ^3Kills^7/^3Deaths^7:^2{}^7/^1{} ^3Damage^7:^2{}^7/^1{}"
                         .format(player.id, player,
                                 player.stats.kills, player.stats.deaths, player.stats.damage_dealt,
                                 player.stats.damage_taken))
            else:
                self.msg("^4{} ^6{} ^3Kills^7/^3Deaths^7:^2{}^7/^1{} ^3Damage^7:^2{}^7/^1{}"
                         .format(player.id, player,
                                 player.stats.kills, player.stats.deaths, player.stats.damage_dealt,
                                 player.stats.damage_taken))
        else:
            self.msg("^2{} ^6{} ^3Kills^7/^3Deaths^7:^2{}^7/^1{} ^3Damage^7:^2{}^7/^1{}"
                     .format(player.id, player,
                             player.stats.kills, player.stats.deaths, player.stats.damage_dealt,
                             player.stats.damage_taken))

    @minqlx.thread
    def cmd_game_status(self, player=None, msg=None, channel=None):
        minqlx.console_print("^6Game Status: ^4Map ^1- ^7{} ^5Game Mode ^1- ^7{}"
                             .format(self.get_cvar("mapname"), self._bdm_gtype.upper()))
        teams = self.teams()
        if len(teams["red"] + teams["blue"] + teams["free"] + teams["spectator"]) == 0:
            minqlx.console_print("^3No players connected")
        if self.game.state not in ["in_progress", "countdown"]:
            minqlx.console_print("^3Match is not in progress")
        if self._bdm_gtype in TEAM_BASED_GAMETYPES:
            red_team = []
            blue_team = []
            minqlx.console_print("^1RED^7: ^7{} ^6::: ^4BLUE^7: {}".format(self.game.red_score, self.game.blue_score))
            for player in teams["red"]:
                red_team.append("    ^1{} ^5{} ^6{} ^7{} {} ^2{}^7/^1{} ^2{}^7/^1{}"
                                .format(player.id, player.stats.ping, player.stats.score, player,
                                        "^7(^2ALIVE^7)" if player.is_alive else "^7(^1DEAD^7)",
                                        player.stats.kills, player.stats.deaths, player.stats.damage_dealt,
                                        player.stats.damage_taken))
            minqlx.console_print("^1Red^7: ^7(^1ID ^5Ping ^6Score ^7Name ^2Kills^7/^1Deaths ^2DmgDlt^7/^1DmgTkn^7)"
                                 " ^1{} ^7Players"
                                 .format(len(red_team)))
            for player in red_team:
                minqlx.console_print(player)
            for player in teams["blue"]:
                blue_team.append("    ^4{} ^5{} ^6{} ^7{} {} ^2{}^7/^1{} ^2{}^7/^1{}"
                                 .format(player.id, player.stats.ping, player.stats.score, player,
                                         "^7(^2ALIVE^7)" if player.is_alive else "^7(^1DEAD^7)",
                                         player.stats.kills, player.stats.deaths, player.stats.damage_dealt,
                                         player.stats.damage_taken))
            minqlx.console_print("^4Blue^7: ^7(^4ID ^5Ping ^6Score ^7Name ^2Kills^7/^1Deaths ^2DmgDlt^7/^1DmgTkn^7)"
                                 " ^4{} ^7Players"
                                 .format(len(blue_team)))
            for player in blue_team:
                minqlx.console_print(player)
        else:
            for player in teams["free"]:
                minqlx.console_print("{}^7: {} ^6Ping^7: {}".format(player, player.stats.score, player.stats.ping))
        for player in teams["spectator"]:
            minqlx.console_print("^6Spectator^7: {} {}".format(player.id, player))

    # ==============================================
    #               Script Commands
    # ==============================================
    @minqlx.thread
    def check_force_switch_vote(self, caller, vote):
        self.callvote("qlx {}mark_agree".format(self.get_cvar("qlx_commandPrefix")),
                      "Force the suggested player switch?")
        minqlx.client_command(caller.id, "vote yes")
        self.msg("{}^7 called vote /cv {}".format(caller.name, vote))
        voter_perc = self.get_cvar("qlx_bdmPlayerPercForVote", int)
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

    def check_entry_exists(self, player, game_type, field):
        return self.db.exists(BDM_KEY.format(player.steam_id, game_type, field))

    def get_bdm_field(self, player, game_type, field):
        if self.db.exists(BDM_KEY.format(player.steam_id, game_type, field)):
            value = self.db.get(BDM_KEY.format(player.steam_id, game_type, field))
        else:
            if field == "rating":
                value = self.get_cvar("qlx_bdmDefaultBDM", int)
            else:
                value = 0
        try:
            data = int(value)
        except ValueError:
            split_rating = value.split(".")
            data = int(split_rating[0])
        return data

    def get_db_field(self, player, field):
        value = None
        data = None
        if self.db.exists(field.format(player.steam_id)):
            value = self.db.get(field.format(player.steam_id))
        if value:
            try:
                data = int(value)
            except ValueError:
                data = value
        return data

    def set_bdm_field(self, player, game_type, field, data, overwrite=True):
        if overwrite:
            self.db.set(BDM_KEY.format(player.steam_id, game_type, field), str(data))
        else:
            self.db.setnx(BDM_KEY.format(player.steam_id, game_type, field), str(data))

    def record_ctf_events(self, sid, medal):
        with self.lock:
            if sid not in self._record_events:
                self._record_events[sid] = {}
                self._record_events[sid]["CAPTURES"] = 0
                self._record_events[sid]["DEFENSES"] = 0
                self._record_events[sid]["ASSISTS"] = 0
            if medal == "CAPTURE":
                self._record_events[sid]["CAPTURES"] += 1
            elif medal == "DEFENSE":
                self._record_events[sid]["DEFENSES"] += 1
            elif medal == "ASSIST":
                self._record_events[sid]["ASSISTS"] += 1

    def record_ft_events(self, stats):
        with self.lock:
            sid = None
            if stats["TYPE"] == "PLAYER_KILL":
                sid = stats["DATA"]["KILLER"]["STEAM_ID"]
            elif stats["TYPE"] == "PLAYER_DEATH":
                sid = stats["DATA"]["VICTIM"]["STEAM_ID"]
            elif stats["TYPE"] == "PLAYER_MEDAL":
                sid = stats["DATA"]["STEAM_ID"]
            if sid:
                if sid not in self._record_events:
                    self._record_events[sid] = {}
                    self._record_events[sid]["KILLS"] = 0
                    self._record_events[sid]["TIMES_FROZEN"] = 0
                    self._record_events[sid]["THAWS"] = 0
                if stats["TYPE"] == "PLAYER_KILL":
                    self._record_events[sid]["KILLS"] += 1
                if stats["TYPE"] == "PLAYER_DEATH" and not stats["DATA"]["SUICIDE"]:
                    self._record_events[sid]["TIMES_FROZEN"] += 1
                if stats["TYPE"] == "PLAYER_MEDAL" and stats["DATA"]["MEDAL"] == "ASSIST":
                    self._record_events[sid]["THAWS"] += 1

    def player_disconnect_record(self, player):
        sid = str(player[0].steam_id)
        if sid[0] == "9":
            return
        with self.lock:
            if self.game.state != "in_progress":
                self._disconnected_players.pop(sid, None)
                self._played_time.pop(sid, None)
                self._team_switchers.pop(sid, None)
                self._spectating_players.pop(sid, None)
                return
            if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                if self.check_dict_value_greater(self._played_time, sid, "time", 0):
                    if sid in self._team_switchers:
                        self._disconnected_players[sid] = {}
                        self._disconnected_players[sid]["score"] = \
                            player[1].score + self._team_switchers[sid]["score"]
                        self._disconnected_players[sid]["kills"] = \
                            player[1].kills + self._team_switchers[sid]["kills"]
                        self._disconnected_players[sid]["deaths"] = \
                            player[1].deaths + self._team_switchers[sid]["deaths"]
                        self._disconnected_players[sid]["damage_dealt"] = \
                            player[1].damage_dealt + self._team_switchers[sid]["damage_dealt"]
                        self._disconnected_players[sid]["damage_taken"] = \
                            player[1].damage_taken + self._team_switchers[sid]["damage_taken"]
                        self._disconnected_players[sid]["time"] = \
                            player[1].time + self._team_switchers[sid]["time"]
                        self._team_switchers.pop(sid, None)
                    else:
                        self._disconnected_players[sid] = {}
                        self._disconnected_players[sid]["score"] = player[1].score
                        self._disconnected_players[sid]["kills"] = player[1].kills
                        self._disconnected_players[sid]["deaths"] = player[1].deaths
                        self._disconnected_players[sid]["damage_dealt"] = player[1].damage_dealt
                        self._disconnected_players[sid]["damage_taken"] = player[1].damage_taken
                        self._disconnected_players[sid]["time"] = player[1].time
                else:
                    self._disconnected_players[sid] = {}
                    self._disconnected_players[sid]["score"] = player[1].score
                    self._disconnected_players[sid]["kills"] = player[1].kills
                    self._disconnected_players[sid]["deaths"] = player[1].deaths
                    self._disconnected_players[sid]["damage_dealt"] = player[1].damage_dealt
                    self._disconnected_players[sid]["damage_taken"] = player[1].damage_taken
                    self._disconnected_players[sid]["time"] = player[1].time
                self._played_time.pop(sid, None)
                self._team_switchers.pop(sid, None)
                self._spectating_players.pop(sid, None)
            else:
                self._disconnected_players[sid] = {}
                self._disconnected_players[sid]["score"] = player[1].score
                self._disconnected_players[sid]["kills"] = player[1].kills
                self._disconnected_players[sid]["deaths"] = player[1].deaths
                self._disconnected_players[sid]["damage_dealt"] = player[1].damage_dealt
                self._disconnected_players[sid]["damage_taken"] = player[1].damage_taken
                self._disconnected_players[sid]["time"] = player[1].time
                self._played_time.pop(sid, None)
                self._team_switchers.pop(sid, None)
                self._spectating_players.pop(sid, None)

    @minqlx.next_frame
    def team_switch_record(self, player, new_team, old_team):
        sid = str(player.steam_id)
        if sid[0] == "9":
            return
        if self._bdm_gtype in TEAM_BASED_GAMETYPES:
            if self.game.state != "in_progress":
                return
            with self.lock:
                if old_team != "spectator" and new_team == "spectator":
                    if self.check_dict_value_greater(self._played_time, sid, "time", 0):
                        self._spectating_players[sid] = {}
                        self._spectating_players[sid]["score"] =\
                            self._played_time[sid]["score"]
                        self._spectating_players[sid]["kills"] =\
                            self._played_time[sid]["kills"]
                        self._spectating_players[sid]["deaths"] =\
                            self._played_time[sid]["deaths"]
                        self._spectating_players[sid]["damage_dealt"] =\
                            self._played_time[sid]["damage_dealt"]
                        self._spectating_players[sid]["damage_taken"] =\
                            self._played_time[sid]["damage_taken"]
                        self._spectating_players[sid]["time"] =\
                            self._played_time[sid]["time"]
                    self._played_time.pop(sid, None)
                elif old_team == "spectator" and new_team != "spectator":
                    if self.check_dict_value_greater(self._spectating_players, sid, "time", 0):
                        self._team_switchers[sid] = {}
                        self._team_switchers[sid]["score"] =\
                            self._spectating_players[sid]["score"]
                        self._team_switchers[sid]["kills"] =\
                            self._spectating_players[sid]["kills"]
                        self._team_switchers[sid]["deaths"] =\
                            self._spectating_players[sid]["deaths"]
                        self._team_switchers[sid]["damage_dealt"] =\
                            self._spectating_players[sid]["damage_dealt"]
                        self._team_switchers[sid]["damage_taken"] =\
                            self._spectating_players[sid]["damage_taken"]
                        self._team_switchers[sid]["time"] =\
                            self._spectating_players[sid]["time"]
                        self._spectating_players.pop(sid, None)
                        self._played_time[sid]["team"] = new_team
                    else:
                        self._played_time[sid] = {}
                        self._played_time[sid]["team"] = new_team
                        self._played_time[sid]["score"] = 0
                        self._played_time[sid]["kills"] = 0
                        self._played_time[sid]["deaths"] = 0
                        self._played_time[sid]["damage_dealt"] = 0
                        self._played_time[sid]["damage_taken"] = 0
                        self._played_time[sid]["time"] = 0
                else:
                    if sid in self._team_switchers:
                        self._team_switchers[sid]["score"] +=\
                            self._team_switchers[sid]["score"] + self._played_time[sid]["score"]
                        self._team_switchers[sid]["kills"] +=\
                            self._team_switchers[sid]["kills"] + self._played_time[sid]["kills"]
                        self._team_switchers[sid]["deaths"] +=\
                            self._team_switchers[sid]["deaths"] + self._played_time[sid]["deaths"]
                        self._team_switchers[sid]["damage_dealt"] +=\
                            self._team_switchers[sid]["damage_dealt"] + self._played_time[sid]["damage_dealt"]
                        self._team_switchers[sid]["damage_taken"] +=\
                            self._team_switchers[sid]["damage_taken"] + self._played_time[sid]["damage_taken"]
                        self._team_switchers[sid]["time"] +=\
                            self._team_switchers[sid]["time"] + self._played_time[sid]["time"]
                    else:
                        self._team_switchers[sid] = {}
                        self._team_switchers[sid]["score"] = self._played_time[sid]["score"]
                        self._team_switchers[sid]["kills"] = self._played_time[sid]["kills"]
                        self._team_switchers[sid]["deaths"] = self._played_time[sid]["deaths"]
                        self._team_switchers[sid]["damage_dealt"] = self._played_time[sid]["damage_dealt"]
                        self._team_switchers[sid]["damage_taken"] = self._played_time[sid]["damage_taken"]
                        self._team_switchers[sid]["time"] = self._played_time[sid]["time"]
                    self._played_time[sid]["team"] = new_team

    def reset_data(self):
        self._played_time.clear()
        self._disconnected_players.clear()
        self._team_switchers.clear()
        self._spectating_players.clear()
        self._match_stats.clear()
        self._player_stats.clear()
        self._record_events.clear()
        self.game_active = False
        self.rounds_played = 0

    def suggest_switch(self, teams):
        red_bdm = self.team_average(teams["red"])
        blue_bdm = self.team_average(teams["blue"])
        difference = round(abs(red_bdm - blue_bdm))
        diff = 99999
        new_difference = 99999
        players = None
        for red in teams["red"]:
            for blue in teams["blue"]:
                temp_red = teams["red"].copy()
                temp_blue = teams["blue"].copy()
                temp_red.append(blue)
                temp_blue.append(red)
                temp_red.remove(red)
                temp_blue.remove(blue)
                avg_red = self.team_average(temp_red)
                avg_blue = self.team_average(temp_blue)
                if abs(avg_red - avg_blue) < diff:
                    new_difference = round(abs(avg_red - avg_blue))
                    diff = abs(avg_red - avg_blue)
                    players = (red, blue)
        if new_difference < difference:
            return players
        else:
            return None

    def team_average(self, team):
        """Calculates the average rating of a team."""
        avg = 0
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self._bdm_gtype
        if team:
            for p in team:
                rating = self.get_bdm_field(p, game_type, "rating")
                avg += int(rating)
            avg /= len(team)
        return round(avg)

    def clear_suggestion(self):
        self._agreeing_players = None
        self._players_agree = [False, False]

    def execute_switch(self):
        if not self.get_cvar("qlx_bdmEnableSwitch", bool):
            self.msg("^4This script is still collecting data.")
            self.msg("^4The server admin will enable this switch function when enough data has been collected.")
        elif self._agreeing_players:
            player1 = self.player(int(self._agreeing_players[0]))
            player2 = self.player(int(self._agreeing_players[1]))
            try:
                player1.update()
                player2.update()
            except Exception as e:
                minqlx.console_print("^1Exception: {}".format(e))
                return
            if player1.team != "spectator" and player2.team != "spectator":
                self.switch(player1, player2)
        self._agreeing_players = None
        self._players_agree = [False, False]
        self._suggested_switch = 0

    @minqlx.thread
    def save_previous(self):
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self._bdm_gtype
        for player in self._save_previous_bdm:
            for x in range(5, 1, -1):
                if self.db.exists(BDM_KEY.format(player, game_type, "rating{}".format(x - 1))):
                    rating = self.db.get(BDM_KEY.format(player, game_type, "rating{}".format(x - 1)))
                    self.db.set(BDM_KEY.format(player, game_type, "rating{}".format(x)), rating)
            self.db.set(BDM_KEY.format(player, game_type, "rating1"), self._save_previous_bdm[player])
        self._save_previous_bdm = {}

    @minqlx.thread
    def round_stats_record(self):
        teams = self.teams()
        with self.lock:
            for player in teams["red"]:
                sid = str(player.steam_id)
                if sid[0] == "9":
                    continue
                stats = player.stats
                self._played_time[sid]["score"] = stats.score
                self._played_time[sid]["kills"] = stats.kills
                self._played_time[sid]["deaths"] = stats.deaths
                self._played_time[sid]["damage_dealt"] = stats.damage_dealt
                self._played_time[sid]["damage_taken"] = stats.damage_taken
                self._played_time[sid]["time"] = stats.time
            for player in teams["blue"]:
                sid = str(player.steam_id)
                if sid[0] == "9":
                    continue
                stats = player.stats
                self._played_time[sid]["score"] = stats.score
                self._played_time[sid]["kills"] = stats.kills
                self._played_time[sid]["deaths"] = stats.deaths
                self._played_time[sid]["damage_dealt"] = stats.damage_dealt
                self._played_time[sid]["damage_taken"] = stats.damage_taken
                self._played_time[sid]["time"] = stats.time

    @minqlx.delay(2)
    def players_in_teams(self):
        with self.lock:
            self._played_time.clear()
            self._disconnected_players.clear()
            self._team_switchers.clear()
            self._spectating_players.clear()
            self._record_events.clear()
            if self._bdm_gtype in BDM_GAMETYPES:
                teams = self.teams()
                if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                    for player in teams["red"]:
                        sid = str(player.steam_id)
                        if sid[0] == "9":
                            continue
                        self._played_time[sid] = {}
                        self._played_time[sid]["team"] = "red"
                        self._played_time[sid]["score"] = 0
                        self._played_time[sid]["kills"] = 0
                        self._played_time[sid]["deaths"] = 0
                        self._played_time[sid]["damage_dealt"] = 0
                        self._played_time[sid]["damage_taken"] = 0
                        self._played_time[sid]["time"] = 0
                    for player in teams["blue"]:
                        sid = str(player.steam_id)
                        if sid[0] == "9":
                            continue
                        self._played_time[sid] = {}
                        self._played_time[sid]["team"] = "blue"
                        self._played_time[sid]["score"] = 0
                        self._played_time[sid]["kills"] = 0
                        self._played_time[sid]["deaths"] = 0
                        self._played_time[sid]["damage_dealt"] = 0
                        self._played_time[sid]["damage_taken"] = 0
                        self._played_time[sid]["time"] = 0

                else:
                    for player in teams["free"]:
                        sid = str(player.steam_id)
                        if sid[0] == "9":
                            continue
                        self._played_time[sid] = {}
                        self._played_time[sid]["team"] = "free"
                        self._played_time[sid]["score"] = 0
                        self._played_time[sid]["kills"] = 0
                        self._played_time[sid]["deaths"] = 0
                        self._played_time[sid]["damage_dealt"] = 0
                        self._played_time[sid]["damage_taken"] = 0
                        self._played_time[sid]["time"] = 0

    def create_db(self):
        players = self.players()
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self._bdm_gtype
        for player in players:
            sid = str(player.steam_id)
            if sid[0] == "9":
                continue
            self.set_bdm_field(player, game_type, "rating", self.get_cvar("qlx_bdmDefaultBDM"), False)
            self.set_bdm_field(player, game_type, "games_completed", "0", False)
            self.set_bdm_field(player, game_type, "games_left", "0", False)

    # noinspection PyMethodMayBeStatic
    def check_dict_value_greater(self, dic, sid, key, check_against):
        try:
            return dic[sid][key] > check_against
        except KeyError:
            return False

    @minqlx.thread
    def process_game(self):
        with self.lock:
            teams = self.teams()
            game_time = int(round(time.time() * 1000)) - self.game_start
            match_time = 0
            self.game_active = False
            self._save_previous_bdm = {}
            self._player_stats = {}
            self._match_stats = {}
            self._player_stats["DmgASum"] = 0
            self._player_stats["bdmSum"] = 0
            match_perc = self.get_cvar("qlx_bdmMinTimePerc", int) / 100.0

            if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                self.player_count = 0
                if self._bdm_gtype in ROUND_BASED_GAMETYPES:
                    if self.rounds_played < self.get_cvar("qlx_bdmMinRounds", int):
                        minqlx.console_print("--- Only {} rounds played but need {} rounds,"
                                             " BDM is not being calculated ---"
                                             .format(self.rounds_played, self.get_cvar("qlx_bdmMinRounds", int)))
                        return

                for player in teams["red"] + teams["blue"]:
                    sid = str(player.steam_id)
                    if sid[0] == "9":
                        continue
                    stats = player.stats
                    self._match_stats[sid] = {}
                    self._match_stats[sid]["score"] = stats.score
                    self._match_stats[sid]["kills"] = stats.kills
                    self._match_stats[sid]["deaths"] = stats.deaths
                    self._match_stats[sid]["damage_dealt"] = stats.damage_dealt
                    self._match_stats[sid]["damage_taken"] = stats.damage_taken
                    self._match_stats[sid]["time"] = stats.time
                    if self._match_stats[sid]["time"] > match_time:
                        match_time = self._match_stats[sid]["time"]
                if game_time > match_time:
                    match_time = game_time
                needed_time = match_time * match_perc

                finished_calc = False
                if self._bdm_gtype == "ca":
                    finished_calc = self.calc_ca_dmga(needed_time, match_time)
                elif self._bdm_gtype == "ft":
                    finished_calc = self.calc_ft_dmga(needed_time, match_time)
                elif self._bdm_gtype == "ctf":
                    finished_calc = self.calc_ctf_dmga(needed_time, match_time)
                elif self._bdm_gtype == "tdm":
                    finished_calc = self.calc_tdm_dmga(needed_time, match_time)

                if not finished_calc:
                    if self.get_cvar("g_factory").lower() == "ictf":
                        game_type = "ictf"
                    else:
                        game_type = self._bdm_gtype
                    minqlx.console_print("^1Error ^7calculating ^2{} ^7DmgA.".format(game_type))
                    return

                if self.player_count < (self.get_cvar("qlx_bdmMinimumTeamSize", int) * 2):
                    minqlx.console_print("--- There are only {} players on each team, {} are needed. "
                                         "BDM stats not being calculated ---"
                                         .format(int(round(self.player_count / 2)),
                                                 self.get_cvar("qlx_bdmMinimumTeamSize", int)))
                    return

            else:
                if self._bdm_gtype == "ffa":
                    for player in teams["free"]:
                        sid = str(player.steam_id)
                        if sid[0] == "9":
                            continue
                        stats = player.stats
                        self._match_stats[sid] = {}
                        self._match_stats[sid]["score"] = stats.score
                        self._match_stats[sid]["kills"] = stats.kills
                        self._match_stats[sid]["deaths"] = stats.deaths
                        self._match_stats[sid]["damage_dealt"] = stats.damage_dealt
                        self._match_stats[sid]["damage_taken"] = stats.damage_taken
                        self._match_stats[sid]["time"] = stats.time
                        if self._match_stats[sid]["time"] > match_time:
                            match_time = self._match_stats[sid]["time"]
                    if game_time > match_time:
                        match_time = game_time
                    needed_time = match_time * match_perc
                    finished_calc = self.calc_ffa_dmga(needed_time, match_time)
                    if not finished_calc:
                        minqlx.console_print("^1Error ^7calculating ^2{} ^7DmgA.".format(self._bdm_gtype))
                        return
            # Calculate New BDMs based on DmgA calculations
            self.calc_new_bdm()

    def calc_ffa_dmga(self, needed_time, match_time):
        per_kill_pts = self.get_cvar("qlx_bdmFfaKillPts", int)
        for sid in self._disconnected_players:
            if self._disconnected_players[sid]["time"] >= needed_time:
                self._player_stats[sid] = {}
                self._player_stats[sid]["left_game"] = 1
                self._player_stats[sid]["DmgA"] = ((self._disconnected_players[sid]["damage_dealt"] +
                                                    self._disconnected_players[sid]["kills"] * per_kill_pts) *
                                                   match_time / self._disconnected_players[sid]["time"])
                self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))

        for sid in self._match_stats:
            if self._match_stats[sid]["time"] >= needed_time:
                self._player_stats[sid] = {}
                self._player_stats[sid]["left_game"] = 0
                self._player_stats[sid]["DmgA"] = ((self._match_stats[sid]["damage_dealt"] +
                                                    self._match_stats[sid]["kills"] * per_kill_pts) *
                                                   match_time / self._match_stats[sid]["time"])
                self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))
        return True

    def calc_ca_dmga(self, needed_time, match_time):
        per_kill_pts = self.get_cvar("qlx_bdmCaKillPts", int)
        dmg_rcvd_perc = self.get_cvar("qlx_bdmDamageRcvdPerc", int) / 100.0
        for sid in self._disconnected_players:
            if self._disconnected_players[sid]["time"] >= needed_time:
                self.player_count += 1
                self._player_stats[sid] = {}
                self._player_stats[sid]["left_game"] = 1
                self._player_stats[sid]["DmgA"] = ((self._disconnected_players[sid]["damage_dealt"] +
                                                    (self._disconnected_players[sid]["kills"] * per_kill_pts) -
                                                    (self._disconnected_players[sid]["damage_taken"] * dmg_rcvd_perc)) *
                                                   match_time / self._disconnected_players[sid]["time"])
                self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))

        for sid in self._spectating_players:
            if self._spectating_players[sid]["time"] >= needed_time:
                self.player_count += 1
                self._player_stats[sid] = {}
                self._player_stats[sid]["left_game"] = 1
                self._player_stats[sid]["DmgA"] = ((self._spectating_players[sid]["damage_dealt"] +
                                                    (self._spectating_players[sid]["kills"] * per_kill_pts) -
                                                    (self._spectating_players[sid]["damage_taken"] * dmg_rcvd_perc)) *
                                                   match_time / self._spectating_players[sid]["time"])
                self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))

        for sid in self._match_stats:
            if sid in self._team_switchers:
                play_time = self._match_stats[sid]["time"] + self._team_switchers[sid]["time"]
                if play_time >= needed_time:
                    self.player_count += 1
                    damage_dealt = self._match_stats[sid]["damage_dealt"] + self._team_switchers[sid]["damage_dealt"]
                    kills = self._match_stats[sid]["kills"] + self._team_switchers[sid]["kills"]
                    damage_taken = self._match_stats[sid]["damage_taken"] + self._team_switchers[sid]["damage_taken"]
                    self._player_stats[sid] = {}
                    self._player_stats[sid]["left_game"] = 0
                    self._player_stats[sid]["DmgA"] = ((damage_dealt + (kills * per_kill_pts) -
                                                        (damage_taken * dmg_rcvd_perc)) * match_time / play_time)
                    self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                    self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))
            else:
                if self._match_stats[sid]["time"] >= needed_time:
                    self.player_count += 1
                    self._player_stats[sid] = {}
                    self._player_stats[sid]["left_game"] = 0
                    self._player_stats[sid]["DmgA"] = ((self._match_stats[sid]["damage_dealt"] +
                                                        (self._match_stats[sid]["kills"] * per_kill_pts) -
                                                        (self._match_stats[sid]["damage_taken"] *
                                                        dmg_rcvd_perc)) * match_time / self._match_stats[sid]["time"])
                    self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                    self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))
        return True

    def calc_ft_dmga(self, needed_time, match_time):
        per_kill_pts = self.get_cvar("qlx_bdmFtKillPts", int)
        per_thaw_pts = self.get_cvar("qlx_bdmFtThawPts", int)
        per_frozen_pts = self.get_cvar("qlx_bdmFtFrozenPts", int)
        for sid in self._disconnected_players:
            if self._disconnected_players[sid]["time"] >= needed_time:
                self.player_count += 1
                self._player_stats[sid] = {}
                self._player_stats[sid]["left_game"] = 1
                if sid in self._record_events:
                    p_kills = self._record_events[sid]["KILLS"]
                    p_thaws = self._record_events[sid]["THAWS"]
                    p_frozen = self._record_events[sid]["TIMES_FROZEN"]
                else:
                    p_kills = 0
                    p_thaws = 0
                    p_frozen = 0
                self._player_stats[sid]["DmgA"] = ((self._disconnected_players[sid]["damage_dealt"] +
                                                   (p_kills * per_kill_pts) +
                                                   (p_thaws * per_thaw_pts) -
                                                   (p_frozen * per_frozen_pts)) *
                                                   match_time / self._disconnected_players[sid]["time"])
                self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))

        for sid in self._spectating_players:
            if self._spectating_players[sid]["time"] >= needed_time:
                self.player_count += 1
                self._player_stats[sid] = {}
                self._player_stats[sid]["left_game"] = 1
                if sid in self._record_events:
                    p_kills = self._record_events[sid]["KILLS"]
                    p_thaws = self._record_events[sid]["THAWS"]
                    p_frozen = self._record_events[sid]["TIMES_FROZEN"]
                else:
                    p_kills = 0
                    p_thaws = 0
                    p_frozen = 0
                self._player_stats[sid]["DmgA"] = ((self._spectating_players[sid]["damage_dealt"] +
                                                   (p_kills * per_kill_pts) +
                                                   (p_thaws * per_thaw_pts) -
                                                   (p_frozen * per_frozen_pts)) *
                                                   match_time / self._spectating_players[sid]["time"])
                self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))

        for sid in self._match_stats:
            if sid in self._team_switchers:
                play_time = self._match_stats[sid]["time"] + self._team_switchers[sid]["time"]
                if play_time >= needed_time:
                    self.player_count += 1
                    damage_dealt = self._match_stats[sid]["damage_dealt"] + self._team_switchers[sid]["damage_dealt"]
                    self._player_stats[sid] = {}
                    self._player_stats[sid]["left_game"] = 0
                    if sid in self._record_events:
                        p_kills = self._record_events[sid]["KILLS"]
                        p_thaws = self._record_events[sid]["THAWS"]
                        p_frozen = self._record_events[sid]["TIMES_FROZEN"]
                    else:
                        p_kills = 0
                        p_thaws = 0
                        p_frozen = 0
                    self._player_stats[sid]["DmgA"] = ((damage_dealt +
                                                       (p_kills * per_kill_pts) +
                                                       (p_thaws * per_thaw_pts) -
                                                       (p_frozen * per_frozen_pts)) *
                                                       match_time / play_time)
                    self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                    self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))
            else:
                if self._match_stats[sid]["time"] >= needed_time:
                    self.player_count += 1
                    self._player_stats[sid] = {}
                    self._player_stats[sid]["left_game"] = 0
                    if sid in self._record_events:
                        p_kills = self._record_events[sid]["KILLS"]
                        p_thaws = self._record_events[sid]["THAWS"]
                        p_frozen = self._record_events[sid]["TIMES_FROZEN"]
                    else:
                        p_kills = 0
                        p_thaws = 0
                        p_frozen = 0
                    self._player_stats[sid]["DmgA"] = ((self._match_stats[sid]["damage_dealt"] +
                                                       (p_kills * per_kill_pts) +
                                                       (p_thaws * per_thaw_pts) -
                                                       (p_frozen * per_frozen_pts)) *
                                                       match_time / self._match_stats[sid]["time"])
                    self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                    self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))
        return True

    def calc_ctf_dmga(self, needed_time, match_time):
        dmg_rcvd_perc = self.get_cvar("qlx_bdmDamageRcvdPerc", int) / 100.0
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
            per_kill_pts = self.get_cvar("qlx_bdmICtfKillPts", int)
            per_cap_pts = self.get_cvar("qlx_bdmICtfCapPts", int)
            per_assist_pts = self.get_cvar("qlx_bdmICtfAssistPts", int)
            per_defense_pts = self.get_cvar("qlx_bdmICtfDefensePts", int)
        else:
            game_type = "ctf"
            per_kill_pts = self.get_cvar("qlx_bdmCtfKillPts", int)
            per_cap_pts = self.get_cvar("qlx_bdmCtfCapPts", int)
            per_assist_pts = self.get_cvar("qlx_bdmCtfAssistPts", int)
            per_defense_pts = self.get_cvar("qlx_bdmCtfDefensePts", int)

        for sid in self._disconnected_players:
            if self._disconnected_players[sid]["time"] >= needed_time:
                self.player_count += 1
                self._player_stats[sid] = {}
                self._player_stats[sid]["left_game"] = 1
                if sid in self._record_events:
                    p_caps = self._record_events[sid]["CAPTURES"]
                    p_assists = self._record_events[sid]["ASSISTS"]
                    p_defenses = self._record_events[sid]["DEFENSES"]
                else:
                    p_caps = 0
                    p_assists = 0
                    p_defenses = 0
                self._player_stats[sid]["DmgA"] = ((self._disconnected_players[sid]["damage_dealt"] +
                                                   (self._disconnected_players[sid]["kills"] * per_kill_pts) +
                                                   (p_caps * per_cap_pts) +
                                                   (p_assists * per_assist_pts) +
                                                   (p_defenses * per_defense_pts) -
                                                   (self._disconnected_players[sid]["damage_taken"] * dmg_rcvd_perc)) *
                                                   match_time / self._disconnected_players[sid]["time"])
                self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, game_type, "rating")))

        for sid in self._spectating_players:
            if self._spectating_players[sid]["time"] >= needed_time:
                self.player_count += 1
                self._player_stats[sid] = {}
                self._player_stats[sid]["left_game"] = 1
                if sid in self._record_events:
                    p_caps = self._record_events[sid]["CAPTURES"]
                    p_assists = self._record_events[sid]["ASSISTS"]
                    p_defenses = self._record_events[sid]["DEFENSES"]
                else:
                    p_caps = 0
                    p_assists = 0
                    p_defenses = 0
                self._player_stats[sid]["DmgA"] = ((self._spectating_players[sid]["damage_dealt"] +
                                                   (self._match_stats[sid]["kills"] * per_kill_pts) +
                                                   (p_caps * per_cap_pts) +
                                                   (p_assists * per_assist_pts) +
                                                   (p_defenses * per_defense_pts) -
                                                   (self._match_stats[sid]["damage_taken"] * dmg_rcvd_perc)) *
                                                   match_time / self._spectating_players[sid]["time"])
                self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, game_type, "rating")))

        for sid in self._match_stats:
            if sid in self._team_switchers:
                play_time = self._match_stats[sid]["time"] + self._team_switchers[sid]["time"]
                if play_time >= needed_time:
                    self.player_count += 1
                    self._player_stats[sid] = {}
                    self._player_stats[sid]["left_game"] = 0
                    damage_dealt = self._match_stats[sid]["damage_dealt"] + self._team_switchers[sid]["damage_dealt"]
                    kills = self._match_stats[sid]["kills"] + self._team_switchers[sid]["kills"]
                    damage_taken = self._match_stats[sid]["damage_taken"] + self._team_switchers[sid]["damage_taken"]
                    play_time = self._match_stats[sid]["time"] + self._team_switchers[sid]["time"]
                    if sid in self._record_events:
                        p_caps = self._record_events[sid]["CAPTURES"]
                        p_assists = self._record_events[sid]["ASSISTS"]
                        p_defenses = self._record_events[sid]["DEFENSES"]
                    else:
                        p_caps = 0
                        p_assists = 0
                        p_defenses = 0
                    self._player_stats[sid]["DmgA"] = ((damage_dealt +
                                                       (kills * per_kill_pts) +
                                                       (p_caps * per_cap_pts) +
                                                       (p_assists * per_assist_pts) +
                                                       (p_defenses * per_defense_pts) -
                                                       (damage_taken * dmg_rcvd_perc)) * match_time / play_time)
                    self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                    self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, game_type, "rating")))
            else:
                if self._match_stats[sid]["time"] >= needed_time:
                    self.player_count += 1
                    self._player_stats[sid] = {}
                    self._player_stats[sid]["left_game"] = 0
                    if sid in self._record_events:
                        p_caps = self._record_events[sid]["CAPTURES"]
                        p_assists = self._record_events[sid]["ASSISTS"]
                        p_defenses = self._record_events[sid]["DEFENSES"]
                    else:
                        p_caps = 0
                        p_assists = 0
                        p_defenses = 0
                    self._player_stats[sid]["DmgA"] = ((self._match_stats[sid]["damage_dealt"] +
                                                       (self._match_stats[sid]["kills"] * per_kill_pts) +
                                                       (p_caps * per_cap_pts) +
                                                       (p_assists * per_assist_pts) +
                                                       (p_defenses * per_defense_pts) -
                                                       (self._match_stats[sid]["damage_taken"] * dmg_rcvd_perc)) *
                                                       match_time / self._match_stats[sid]["time"])
                    self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                    self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, game_type, "rating")))
        return True

    def calc_tdm_dmga(self, needed_time, match_time):
        per_kill_pts = self.get_cvar("qlx_bdmTdmKillPts", int)
        per_death_pts = self.get_cvar("qlx_bdmTdmDeathPts", int)
        for sid in self._disconnected_players:
            if self._disconnected_players[sid]["time"] >= needed_time:
                self.player_count += 1
                self._player_stats[sid] = {}
                self._player_stats[sid]["left_game"] = 1
                self._player_stats[sid]["DmgA"] = ((self._disconnected_players[sid]["damage_dealt"] +
                                                    (self._disconnected_players[sid]["kills"] * per_kill_pts) -
                                                    (self._disconnected_players[sid]["deaths"] * per_death_pts)) *
                                                   match_time / self._disconnected_players[sid]["time"])
                self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))

        for sid in self._spectating_players:
            if self._spectating_players[sid]["time"] >= needed_time:
                self.player_count += 1
                self._player_stats[sid] = {}
                self._player_stats[sid]["left_game"] = 1
                self._player_stats[sid]["DmgA"] = ((self._spectating_players[sid]["damage_dealt"] +
                                                    (self._spectating_players[sid]["kills"] * per_kill_pts) -
                                                    (self._spectating_players[sid]["deaths"] * per_death_pts)) *
                                                   match_time / self._spectating_players[sid]["time"])
                self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))

        for sid in self._match_stats:
            if sid in self._team_switchers:
                play_time = self._match_stats[sid]["time"] + self._team_switchers[sid]["time"]
                if play_time >= needed_time:
                    self.player_count += 1
                    damage_dealt = self._match_stats[sid]["damage_dealt"] + self._team_switchers[sid]["damage_dealt"]
                    kills = self._match_stats[sid]["kills"] + self._team_switchers[sid]["kills"]
                    deaths = self._match_stats[sid]["deaths"] + self._team_switchers[sid]["deaths"]
                    self._player_stats[sid] = {}
                    self._player_stats[sid]["left_game"] = 0
                    self._player_stats[sid]["DmgA"] = ((damage_dealt + (kills * per_kill_pts) -
                                                        (deaths * per_death_pts)) * match_time / play_time)
                    self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                    self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))
            else:
                if self._match_stats[sid]["time"] >= needed_time:
                    self.player_count += 1
                    self._player_stats[sid] = {}
                    self._player_stats[sid]["left_game"] = 0
                    self._player_stats[sid]["DmgA"] = ((self._match_stats[sid]["damage_dealt"] +
                                                       (self._match_stats[sid]["kills"] * per_kill_pts) -
                                                       (self._match_stats[sid]["deaths"] * per_death_pts)) *
                                                       match_time / self._match_stats[sid]["time"])
                    self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                    self._player_stats["bdmSum"] += int(self.db.get(BDM_KEY.format(sid, self._bdm_gtype, "rating")))
        return True

    def calc_new_bdm(self):
        min_rating = self.get_cvar("qlx_bdmMinRating", int)
        max_rating = self.get_cvar("qlx_bdmMaxRating", int)
        print_change = self.get_cvar("qlx_bdmConsolePrintBdmChange", bool)
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self._bdm_gtype
        for p_sid in self._player_stats:
            if p_sid == "bdmSum" or p_sid == "DmgASum":
                continue
            if self._player_stats[p_sid]["left_game"] == 0:
                self.db.incr(BDM_KEY.format(p_sid, game_type, "games_completed"))
            else:
                self.db.incr(BDM_KEY.format(p_sid, game_type, "games_left"))
            games = int(self.db.get(BDM_KEY.format(p_sid, game_type, "games_completed"))) + \
                int(self.db.get(BDM_KEY.format(p_sid, game_type, "games_left")))
            rating = int(self.db.get(BDM_KEY.format(p_sid, game_type, "rating")))
            games_played = games if games < 30 else 30
            try:
                change = (((self._player_stats[p_sid]["DmgA"] *
                            self._player_stats["bdmSum"] / self._player_stats["DmgASum"]) - rating) / games_played)
            except KeyError:
                change = 0

            new_rating = int(round(rating + change))
            if min_rating >= new_rating:
                new_rating = min_rating
            elif max_rating <= new_rating:
                new_rating = max_rating
            if new_rating != rating:
                self._save_previous_bdm[p_sid] = rating
                self.db.set(BDM_KEY.format(p_sid, game_type, "rating"), str(new_rating))
            if print_change:
                name = self.db.lindex("minqlx:players:{}".format(p_sid), 0)
                minqlx.console_print("^6Player^7: {} ^7BDM Change: Old = ^6{}^7, New = ^2{}"
                                     .format(name, rating, new_rating))
        if len(self._save_previous_bdm) > 0:
            self.save_previous()

    @minqlx.thread
    def set_initial_bdm(self, player, game_type):
        sid = player.steam_id
        response = False
        url = "http://{}/elo/{}".format(ELO_URL, sid)
        attempts = 0
        elo_dict = {}
        while attempts < 3:
            attempts += 1
            info = requests.get(url)
            if info.status_code != requests.codes.ok:
                continue
            info_js = info.json()
            if "players" in info_js:
                attempts = 3
                response = True
        if response:
            elo_dict[sid] = {}
            for record in info_js["players"]:
                for gt in BDM_GAMETYPES:
                    if gt in record:
                        elo_dict[sid][gt] = record[str(gt)]["elo"]
                    else:
                        elo_dict[sid][gt] = 1200

            m = self.get_cvar("qlx_bdmMCalculation", float)
            b = self.get_cvar("qlx_bdmBCalculation", float)
            if game_type in elo_dict[sid]:
                bdm = int(m * int(elo_dict[sid][game_type]) + b)
            else:
                bdm = self.get_cvar("qlx_bdmDefaultBDM", int)
            if bdm < self.get_cvar("qlx_bdmMinRating", int):
                bdm = self.get_cvar("qlx_bdmMinRating", int)
            elif bdm > self.get_cvar("qlx_bdmMaxRating", int):
                bdm = self.get_cvar("qlx_bdmMaxRating", int)
            self.db.set(BDM_KEY.format(sid, game_type, "rating"), str(bdm))
