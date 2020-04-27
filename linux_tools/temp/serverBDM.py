# serverBDM.py is a plugin for minqlx to:
# - Calculate and store players Basic Damage Metric (BDM) on the server.
# - It is a server side skill calculation similar to ELO.
# - Since it is server side your BDM is based only on performance on each individual server.

# created by BarelyMiSSeD on 5-5-2018
#
"""
# **** If you don't want to enable the !teams and !balance commands in this plugin (still using it from another plugin)
# You need to disable qlx_bdmRespondToTeamsCommand and qlx_bdmRespondToBalanceCommand (enabled by default) ****
# Balancing after shuffle vote is enabled by default. Disable qlx_bdmBalanceAfterShuffleVote to turn this off.


// **** CVARs **** Copy after this line into your server config
// Minqlx Bot Permission level needed to perform admin functions
set qlx_bdmAdmin "3"
// The default BDM rating given to new players if initial BDM is not calculated from retreiving ELO
set qlx_bdmDefaultBDM "1022"
// The minimum BDM rating (if calculated BDM falls below this, this value will be set)
set qlx_bdmMinRating "300"
// The maximum BDM rating (if calculated BDM goes above this, this value will be set)
set qlx_bdmMaxRating "3000"
// This will lock the teams whenever a regular BDM balance is done. (0=disable, 1=enable)
// (Using !balance, !bbalance, or during game countdown auto-balance)
//   (NOTE: A pre-balance always locks the teams. Using !prebalance or the pre-game initialization auto-balance.)
set qlx_bdmLockTeamsForBalance "0"
// Balance with BDM Ratings at the start of a team game
//   This will disable shuffle vote calling (0=disable, 1=enable).
set qlx_bdmBalanceAtGameStart "0"
// Allow game to start without balanced teams. Requires qlx_bdmBalanceAtGameStart to be enabled.
//  Sets g_teamForceBalance to 0 so players can ready up even if teams are not even. (only sets at load time)
//  If qlx_bdmBalanceAtGameStart or qlx_bdmAllowUnevenTeamsReady are not enabled g_teamForceBalance will be set to 1
set qlx_bdmAllowUnevenTeamsReady "1"
// balance the teams based on BDM after a shuffle vote passes
set qlx_bdmBalanceAfterShuffleVote "1"
// Balance teams if the teams are not even
set qlx_bdmBalanceUnevenTeams "1"
// Minimum team BDM Average Difference before a player switch is suggested
set qlx_bdmMinimumSuggestionDiff "60"
// Print the BDM change results to the server console at the completion of BDM calculations
set qlx_bdmConsolePrintBdmChange "1"
// Enable the player switch that is gotten from !bteams
//   This feature is so the !bteams function can be seen by players but not enabled
//   until the server admin decides enough stats have been collected
set qlx_bdmEnableSwitch "1"
// Set BDM to respond to the !teams bot command, if this is not enabled the !teams command will reset
//  any suggested switch made from the !bteams command
set qlx_bdmRespondToTeamsCommand "1"
// Set BDM to respond to the !balance bot command
set qlx_bdmRespondToBalanceCommand "1"
// Modify server response to Elo type commands (0=leave elo commands alone, 1=disable elo comands, 2=tell of bdm usage)
set qlx_bdmModifyEloCmds "0"
// Set to "1" to enable '/callvote do' on the server to allow voting to force the suggested switch from !bteams
set qlx_bdmEnableDoVote "1"
// Enable to require a do vote to execute the suggested players switch for NO_COUNTDOWN_GAMESTYPES
//  This requires qlx_bdmEnableDoVote to be enabled or the switch will execute when both players agree.
set qlx_bdmRequireDoVote "0"
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
// *** Wipeout Settings ***
set qlx_bdmWoKillPts "50"
set qlx_bdmWoDeathPts "75"
set qlx_bdmWoMinRounds "3"
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
// Adjust this if the player BDMs are not adjusting enough or is adjusting too much after each game.
// Smaller number results in more BDM change, larger number will result in less BDM change.
set qlx_bdmNumGamesForCalculation "25"

"""

import minqlx
import time
from threading import Timer, Thread
import random
import requests
import re
import multiprocessing

VERSION = "2.03.9"
# TO_BE_ADDED = ("duel", "dom", "ad", "1f", "har")
BDM_GAMETYPES = ("ft", "ca", "ctf", "ffa", "ictf", "tdm", "wipeout")
TEAM_BASED_GAMETYPES = ("ca", "ctf", "ft", "tdm", "ictf", "wipeout")
ROUND_BASED_GAMETYPES = ("ca", "ft", "wipeout")
COUNTDOWN_GAMESTYPES = ("ca", "ft", "wipeout")
NO_COUNTDOWN_GAMESTYPES = ("1f", "ad", "dom", "ctf", "tdm", "har")
BDM_KEY = "minqlx:players:{}:bdm:{}:{}"
ELO_URL = "qlstats.net"

ENABLE_LOG = True  # set to True/False to enable/disable logging

if ENABLE_LOG:
    import logging
    import os
    from logging.handlers import RotatingFileHandler


class serverBDM(minqlx.Plugin):
    def __init__(self):
        if ENABLE_LOG:
            self.bdm_log = logging.Logger(__name__)
            file_dir = os.path.join(minqlx.get_cvar("fs_homepath"), "logs")
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)

            file_path = os.path.join(file_dir, "serverBDM.log")
            file_fmt = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
            file_handler = RotatingFileHandler(file_path, encoding="utf-8", maxBytes=3000000, backupCount=5)
            file_handler.setFormatter(file_fmt)
            self.bdm_log.addHandler(file_handler)
            self.bdm_log.info("============================= Logger started =============================")

        # cvars
        self.set_cvar_once("qlx_bdmAdmin", "3")
        self.set_cvar_once("qlx_bdmDefaultBDM", "1022")
        self.set_cvar_once("qlx_bdmMinRating", "300")
        self.set_cvar_once("qlx_bdmMaxRating", "3000")
        self.set_cvar_once("qlx_bdmLockTeamsForBalance", "0")
        self.set_cvar_once("qlx_bdmBalanceAtGameStart", "0")
        self.set_cvar_once("qlx_bdmAllowUnevenTeamsReady", "1")
        self.set_cvar_once("qlx_bdmBalanceAfterShuffleVote", "1")
        self.set_cvar_once("qlx_bdmMinimumSuggestionDiff", "60")
        self.set_cvar_once("qlx_bdmBalanceUnevenTeams", "1")
        self.set_cvar_once("qlx_bdmConsolePrintBdmChange", "1")
        self.set_cvar_once("qlx_bdmEnableSwitch", "1")
        self.set_cvar_once("qlx_bdmRespondToTeamsCommand", "1")
        self.set_cvar_once("qlx_bdmRespondToBalanceCommand", "1")
        self.set_cvar_once("qlx_bdmModifyEloCmds", "0")
        self.set_cvar_once("qlx_bdmEnableDoVote", "1")
        self.set_cvar_once("qlx_bdmRequireDoVote", "0")
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
        # Wipeout
        self.set_cvar_once("qlx_bdmWoKillPts", "50")
        self.set_cvar_once("qlx_bdmWoDeathPts", "75")
        self.set_cvar_once("qlx_bdmWoMinRounds", "3")
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
        self.set_cvar_once("qlx_bdmNumGamesForCalculation", "15")

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
        self.add_hook("game_countdown", self.handle_game_countdown)
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
        self.add_command("bbalance", self.cmd_bdmbalance, int(minqlx.get_cvar("qlx_bdmAdmin")))
        self.add_command("balance", self.balance_cmd, int(minqlx.get_cvar("qlx_bdmAdmin")))
        self.add_command(("agree", "a"), self.cmd_bdmagree)
        self.add_command("do", self.cmd_bdmdo, int(minqlx.get_cvar("qlx_bdmAdmin")))
        self.add_command("setbdm", self.cmd_set_bdm, int(minqlx.get_cvar("qlx_bdmAdmin")))
        self.add_command("prebalance", self.cd_bdmbalance, int(minqlx.get_cvar("qlx_bdmAdmin")))
        self.add_command("damage", self.cmd_damage_status)
        self.add_command("dmg", self.cmd_dmg_status)
        self.add_command("gamestatus", self.cmd_game_status, int(minqlx.get_cvar("qlx_bdmAdmin")))
        self.add_command("mark_agree", self.cmd_mark_agree, int(minqlx.get_cvar("qlx_bdmAdmin")))
        self.add_command(("elo", "elos"), self.respond_to_elo_requests)

        # Script Variables, Lists, and Dictionaries
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
        self._between_rounds = False
        self._start_countdown = 0
        self._countdown_time = int(minqlx.get_cvar("g_roundWarmupDelay")) / 1000
        self.game_active = False
        self.rounds_played = 0
        self.game_start = 0
        self.player_count = 0
        self.player_join_rating_displayed = []
        self.vote_count = [0, 0, 0]
        self._locked = [False, False]
        self._balance_time = 0
        self._short_ft_countdown = self._bdm_gtype == "ft" and int(minqlx.get_cvar("g_freezeRoundDelay")) <= 1000
        self._end_game_players = {}
        self.cpu_count = multiprocessing.cpu_count()
        self.bdm_changes = []

        # Initializing commands
        if self.game is not None and self.game.state == "in_progress":
            self.players_in_teams()

        if bool(int(minqlx.get_cvar("qlx_bdmBalanceAtGameStart"))) and\
                bool(int(minqlx.get_cvar("qlx_bdmAllowUnevenTeamsReady"))):
            minqlx.console_command('set g_teamForceBalance "0"')
        else:
            minqlx.console_command('set g_teamForceBalance "1"')

        self.remove_conflicting_commands()

    # ==============================================
    #               Event Handler's
    # ==============================================
    def handle_chat(self, player, msg, channel):
        self.process_chat(msg, channel)
        return

    def process_chat(self, msg, channel):
        try:
            if "what is bdm" in msg.lower():
                channel.reply("^6BDM ^7is ^6B^7asic ^6D^7amage ^6M^7etric. It is a server side skill calculation "
                              "similar to ^5ELO^7. Since it is server side your ^6BDM ^7is based only on performance "
                              "on each individual server.\nCommands: ^1{0}bdm^7, ^1{0}bdms^7, ^1{0}bdmh"
                              .format(minqlx.get_cvar("qlx_commandPrefix")))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_chat Exception: {}".format([e]))

    def handle_stats(self, stats):
        self.process_stats(stats)
        return

    def process_stats(self, stats):
        try:
            if (self._locked[0] or self._locked[1]) and time.time() - self._balance_time > 5:
                minqlx.console_command("unlock red")
                self._locked[0] = False
                minqlx.console_command("unlock blue")
                self._locked[1] = False
                self._balance_time = 0
            if self.game is not None and self.game.state != "in_progress":
                return
            if self._bdm_gtype == "ctf" and stats["TYPE"] == "PLAYER_MEDAL":
                self.record_ctf_events(stats["DATA"]["STEAM_ID"], stats["DATA"]["MEDAL"])
            elif self._bdm_gtype == "ft":
                self.record_ft_events(stats)
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_stats Exception: {}".format([e]))

    def handle_player_connect(self, player):
        self.process_player_connect(player)
        return

    def process_player_connect(self, player):
        try:
            sid = str(player.steam_id)
            if sid[0] == "9":
                return
            factory = minqlx.get_cvar("g_factory").lower()
            if factory == "ictf":
                game_type = "ictf"
            elif factory == "wipeout":
                game_type = "wipeout"
            else:
                game_type = self._bdm_gtype
            self.set_bdm_field(player, game_type, "rating", minqlx.get_cvar("qlx_bdmDefaultBDM"), False)
            self.set_bdm_field(player, game_type, "games_completed", "0", False)
            self.set_bdm_field(player, game_type, "games_left", "0", False)
            if bool(int(minqlx.get_cvar("qlx_bdmSetIntitialBDM"))) and\
                    self.get_bdm_field(player, game_type, "games_completed") +\
                    self.get_bdm_field(player, game_type, "games_left") == 0:
                self.set_initial_bdm(player, game_type)
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_player_connect Exception: {}".format([e]))

    def handle_player_loaded(self, player):
        self.process_player_loaded(player)
        return

    def process_player_loaded(self, player):
        try:
            if bool(int(minqlx.get_cvar("qlx_bdmPrintJoinMsg"))):
                sid = str(player.steam_id)
                if sid[0] != "9":
                    if bool(int(minqlx.get_cvar("qlx_bdmPrintBdmStatsEveryMap"))):
                        self.display_join_message(player)
                    else:
                        if sid not in self.player_join_rating_displayed:
                            self.player_join_rating_displayed.append(sid)
                            self.display_join_message(player)
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_player_loaded Exception: {}".format([e]))

    def handle_player_disconnect(self, player, reason):
        self.process_player_disconnect([player, player.stats], player.team)
        try:
            player.update()
        except:
            pass
        return

    def process_player_disconnect(self, player, team):
        try:
            if team != "spectator" and self._suggested_switch == 1:
                self._suggested_switch = -1
            self.player_disconnect_record(player)
            self.player_join_rating_displayed.remove(str(player[0].steam_id))
        except ValueError:
            pass
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_player_disconnect Exception: {}".format([e]))

    def handle_team_switch(self, player, old_team, new_team):
        self.process_team_switch(player, old_team, new_team)
        return

    def process_team_switch(self, player, old_team, new_team):
        try:
            self.team_switch_record(player, new_team, old_team)
            if self._suggested_switch == 1:
                self._suggested_switch = -1
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_team_switch Exception: {}".format([e]))

    def handle_round_countdown(self, number):
        self._start_countdown = time.time()
        self._between_rounds = True
        return

    def handle_round_start(self, number):
        self._start_countdown = 0
        self._between_rounds = False
        if not self.game_active:
            self.rounds_played = 0
            self.game_active = True

    def handle_round_end(self, data):
        self._between_rounds = True
        self.process_round_end(data)
        return

    def process_round_end(self, data):
        try:
            self.rounds_played = int(data["ROUND"])
            if self._bdm_gtype in ROUND_BASED_GAMETYPES:
                if not self.round_stats_record():
                    if ENABLE_LOG:
                        self.bdm_log.info("serverBDM process_round_end call round_stats_record() Error")
                if all(self._players_agree):
                    if self._bdm_gtype in NO_COUNTDOWN_GAMESTYPES or self._short_ft_countdown:
                        self.execute_switch()
                    else:
                        self.execute_switch(True)
            if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                minqlx.console_print("^1RED^7: ^7{} ^6::: ^4BLUE^7: {}"
                                     .format(minqlx.get_configstring(6), minqlx.get_configstring(7)))
            if (self._locked[0] or self._locked[1]) and time.time() - self._balance_time > 5:
                minqlx.console_command("unlock red")
                self._locked[0] = False
                minqlx.console_command("unlock blue")
                self._locked[1] = False
                self._balance_time = 0
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_round_end Exception: {}".format([e]))

    def handle_game_countdown(self):
        self.process_game_countdown()
        return

    def process_game_countdown(self):
        try:
            if bool(int(minqlx.get_cvar("qlx_bdmBalanceAtGameStart"))) and\
                    ((self._bdm_gtype in TEAM_BASED_GAMETYPES and self._bdm_gtype in NO_COUNTDOWN_GAMESTYPES) or
                     self._short_ft_countdown):
                self.msg("^3Performing ^4Pre-Game ^1BDM ^7Auto-Balancing")
                self.cd_bdmbalance()
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_game_countdown Exception: {}".format([e]))

    def handle_game_start(self, data):
        if not self.game_start:
            self.game_start = int(round(time.time() * 1000))
            self.process_game_start()
        return

    def process_game_start(self):
        try:
            self.players_in_teams()
            if self._bdm_gtype == "ft" and int(minqlx.get_cvar("g_freezeRoundDelay")) < 1000:
                return
            if bool(int(minqlx.get_cvar("qlx_bdmBalanceAtGameStart"))) and self._bdm_gtype in TEAM_BASED_GAMETYPES and\
                    self._bdm_gtype in COUNTDOWN_GAMESTYPES and not self._short_ft_countdown:
                self.msg("^3Performing ^1BDM ^7Auto-Balancing")
                self.cmd_bdmbalance()
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_game_start Exception: {}".format([e]))

    def handle_game_end(self, data):
        if data["ABORTED"]:
            self.game_start = 0
            self.reset_data()
            if self._locked[0] or self._locked[1]:
                minqlx.console_command("unlock red")
                self._locked[0] = False
                minqlx.console_command("unlock blue")
                self._locked[1] = False
            self._balance_time = 0
        else:
            self._end_game_players = {}
            teams = self.teams()
            if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                for player in teams["red"] + teams["blue"]:
                    self._end_game_players[player.steam_id] = player.stats
            elif self._bdm_gtype in BDM_GAMETYPES:
                for player in teams["free"]:
                    self._end_game_players[player.steam_id] = player.stats
            game_type = self._bdm_gtype
            factory = minqlx.get_cvar("g_factory").lower()
            if factory == "ictf":
                game_type = "ictf"
            elif factory == "wipeout":
                game_type = "wipeout"
            game_time = int(round(time.time() * 1000)) - self.game_start
            self.game_end_thread(game_type, game_time)

    @minqlx.thread
    def game_end_thread(self, game_type, game_time):
        num = multiprocessing.Value('i', 0)
        old = multiprocessing.Array('i', range(64))
        new = multiprocessing.Array('i', range(64))
        sid = multiprocessing.Array('i', range(64))
        p = multiprocessing.Process(target=self.process_game_end, args=(num, sid, old, new, game_type, game_time,))
        p.start()
        p.join()
        self.print_changes(num, sid, old, new)
        return

    def process_game_end(self, num, sid, old, new, game_type, game_time):
        try:
            time.sleep(0.5)
            self.process_game_data(num, sid, old, new, game_type, game_time)
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM process_game_end Exception: {}".format([e]))

    def handle_vote_called(self, caller, vote, args):
        minqlx.console_print("{} ^7called vote: ^6{} {}".format(caller, vote, args))
        if vote.lower() == "bbalance" or\
                vote.lower() == "balance" and bool(int(minqlx.get_cvar("qlx_bdmRespondToBalanceCommand"))):
            if self.game.state in ["in_progress", "countdown"]:
                self.msg("^3Game is active. Use {}{} to check team balance."
                         .format(minqlx.get_cvar("qlx_commandPrefix"),
                                 "teams" if bool(int(minqlx.get_cvar("qlx_bdmRespondToTeamsCommand"))) else "bteams"))
                return minqlx.RET_STOP_ALL
            self.callvote("qlx {}bbalance".format(minqlx.get_cvar("qlx_commandPrefix")),
                          "Balance Teams based on database stored BDMs?")
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called vote /cv {}".format(caller.name, vote))
            return minqlx.RET_STOP_ALL
        elif vote.lower() == "shuffle":
            if self.game.state in ["in_progress", "countdown"]:
                self.msg("^3Game is active. Shuffle vote denied.")
                return minqlx.RET_STOP_ALL
            elif bool(int(minqlx.get_cvar("qlx_bdmBalanceAtGameStart"))) and self._bdm_gtype in BDM_GAMETYPES:
                self.msg("^3Shuffle vote denied. Teams ^4will be balanced ^3at start of game.")
                return minqlx.RET_STOP_ALL
        elif vote.lower() == "do" and bool(int(minqlx.get_cvar("qlx_bdmEnableDoVote"))) and\
                self._bdm_gtype in TEAM_BASED_GAMETYPES:
            if not self._agreeing_players:
                caller.tell("^3There are no suggested players to switch.")
                return minqlx.RET_STOP_ALL
            self.check_force_switch_vote(caller, vote)
            return minqlx.RET_STOP_ALL

    def handle_vote_count(self, player, yes):
        if self.vote_count[2]:
            self.process_vote_count(yes)
        return

    def process_vote_count(self, yes):
        try:
            if yes:
                self.vote_count[0] += 1
            else:
                self.vote_count[1] += 1
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_vote_count Exception: {}".format([e]))

    def handle_vote_ended(self, votes, vote, args, passed):
        self.process_vote_ended(vote, passed)
        return

    def process_vote_ended(self, vote, passed):
        try:
            self.vote_count[2] = 0
            if passed and vote.lower() == "shuffle" and bool(int(minqlx.get_cvar("qlx_bdmBalanceAfterShuffleVote"))):
                if self._bdm_gtype in TEAM_BASED_GAMETYPES:

                    @minqlx.delay(2.5)
                    def exec_balance():
                        self.msg("^3Shuffle ^7vote passed, ^2Balancing ^1Teams ^7based on ^6BDM ^7stats.")
                        self.cmd_bdmbalance()

                    exec_balance()
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_vote_ended Exception: {}".format([e]))

    def handle_map(self, mapname, factory):
        self.process_map()
        return

    @minqlx.delay(0.3)
    def process_map(self):
        try:
            self.game_start = 0
            self.clear_suggestion()
            self._bdm_gtype = self.game.type_short
            self.reset_data()
            if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                minqlx.console_command("unlock red")
                minqlx.console_command("unlock blue")
            else:
                minqlx.console_command("unlock free")
            self._locked[0] = False
            self._locked[1] = False
            self._balance_time = 0
            self._short_ft_countdown = self._bdm_gtype == "ft" and int(minqlx.get_cvar("g_freezeRoundDelay")) <= 1000
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM handle_map Exception: {}".format([e]))

    # ==============================================
    #               Minqlx Bot Commands
    # ==============================================
    def respond_to_elo_requests(self, player, msg, channel):
        if int(minqlx.get_cvar("qlx_bdmModifyEloCmds")) == 2:
            player.tell("^6This server is using ^1BDM^6, elo information has no impact on BDM teams balancing.")

    def cmd_set_bdm(self, player, msg, channel):
        try:
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
            if rating > int(minqlx.get_cvar("qlx_bdmMaxRating")) or rating < int(minqlx.get_cvar("qlx_bdmMinRating")):
                player.tell("^1Unreasonable player RATING.")
                return minqlx.RET_STOP_ALL
            sid = str(target_player.steam_id)
            if sid[0] == "9":
                player.tell("^1Setting a BOT's BDM is not allowed.")
                return
            factory = minqlx.get_cvar("g_factory").lower()
            if factory == "ictf":
                game_type = "ictf"
            elif factory == "wipeout":
                game_type = "wipeout"
            else:
                game_type = self._bdm_gtype
            self.set_bdm_field(target_player, game_type, "rating", rating)
            player.tell("^4Rating^7: The player {} ^7has been set to a ^4bdm ^7rating of ^1{}^7 for game type {}."
                        .format(target_player, rating, game_type))
            player.tell("^7The rating will be adjusted from this point as games are recorded.")
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM cmd_set_bdm Exception: {}".format([e]))

    def bdm_cmd(self, player, msg, channel):
        try:
            factory = minqlx.get_cvar("g_factory").lower()
            if factory == "ictf":
                game_type = "ictf"
            elif factory == "wipeout":
                game_type = "wipeout"
            else:
                game_type = self._bdm_gtype
            if game_type in BDM_GAMETYPES:
                if len(msg) > 1:
                    try:
                        pid = int(msg[1])
                        p = self.player(pid)
                    except minqlx.NonexistentPlayerError:
                        player.tell("Invalid client ID.")
                        return
                    except ValueError:
                        p, pid = self.find_player(" ".join(msg[1:]))
                        if pid == -1:
                            if p == 0:
                                player.tell("^1Too Many players matched your player name")
                            else:
                                player.tell("^1No player matching that name found")
                            return minqlx.RET_STOP_ALL
                    player = p
                if self.check_entry_exists(player, game_type, "rating"):
                    rating = self.get_bdm_field(player, game_type, "rating")
                    completed = self.get_bdm_field(player, game_type, "games_completed")
                    left = self.get_bdm_field(player, game_type, "games_left")
                    games_here = left + completed
                    channel.reply("^7The ^3{} ^6bdm ^7for {} ^7is ^2{} ^7(games here: ^6{}^7)"
                                  .format(game_type.upper(), player, rating, games_here))
                else:
                    channel.reply("^7There is no stored ^3{} ^6bdm for {}^7. A rating of ^6{} ^7will be used."
                                  .format(game_type.upper(), player, self.default_bdm(player)))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM bdm_cmd Exception: {}".format([e]))

    def bdm_history(self, player, msg, channel):
        try:
            factory = minqlx.get_cvar("g_factory").lower()
            if factory == "ictf":
                game_type = "ictf"
            elif factory == "wipeout":
                game_type = "wipeout"
            else:
                game_type = self._bdm_gtype
            if game_type in BDM_GAMETYPES:
                if len(msg) > 1:
                    try:
                        pid = int(msg[1])
                        p = self.player(pid)
                    except minqlx.NonexistentPlayerError:
                        player.tell("Invalid client ID.")
                        return
                    except ValueError:
                        p, pid = self.find_player(" ".join(msg[1:]))
                        if pid == -1:
                            if p == 0:
                                player.tell("^1Too Many players matched your player name")
                            else:
                                player.tell("^1No player matching that name found")
                            return minqlx.RET_STOP_ALL
                    player = p
                if self.check_entry_exists(player, game_type, "rating"):
                    rating = self.get_bdm_field(player, game_type, "rating")
                    completed = self.get_bdm_field(player, game_type, "games_completed")
                    left = self.get_bdm_field(player, game_type, "games_left")
                    games_here = left + completed
                    if games_here > 0:
                        quit_perc = float(left) / float(games_here) * 100
                    else:
                        quit_perc = 0
                    channel.reply("^7The ^3{0} ^6bdm ^7for {1} ^7is ^2{2} ^7(games here: ^6{3} ^7Quit: ^6{4:.1f}％^7)"
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
                                  .format(self._bdm_gtype.upper(), player, self.default_bdm(player)))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM bdm_history Exception: {}".format([e]))

    def bdms_cmd(self, player, msg, channel):
        self.get_bdms(player, msg, channel)

    @minqlx.thread
    def get_bdms(self, player, msg, channel):
        try:
            if self._bdm_gtype in BDM_GAMETYPES:
                if len(self.players()) == 0:
                    self.msg("^7There are no players connected.")
                    return
                factory = minqlx.get_cvar("g_factory").lower()
                if factory == "ictf":
                    game_type = "ictf"
                elif factory == "wipeout":
                    game_type = "wipeout"
                else:
                    game_type = self._bdm_gtype
                teams = self.teams()
                clients = len(teams["red"])
                if clients:
                    r_players = []
                    r_msg = []
                    for p in teams["red"]:
                        r_players.append([self.get_bdm_field(p, game_type, "rating"), re.sub(r"\^[0-9]", "", p.name)])
                    r_players = sorted(r_players, reverse=True)
                    for r, p in r_players:
                        r_msg.append("^7{}^5:^1{}".format(p, r))
                    self.msg("^7, ".join(r_msg))

                clients = len(teams["blue"])
                if clients:
                    b_players = []
                    b_msg = []
                    for p in teams["blue"]:
                        b_players.append([self.get_bdm_field(p, game_type, "rating"), re.sub(r"\^[0-9]", "", p.name)])
                    b_players = sorted(b_players, reverse=True)
                    for r, p in b_players:
                        b_msg.append("^7{}^5:^4{}".format(p, r))
                    self.msg("^7, ".join(b_msg))

                clients = len(teams["free"])
                if clients:
                    f_players = []
                    f_msg = []
                    for p in teams["free"]:
                        f_players.append([self.get_bdm_field(p, game_type, "rating"), re.sub(r"\^[0-9]", "", p.name)])
                    f_players = sorted(f_players, reverse=True)
                    for r, p in f_players:
                        f_msg.append("^7{}^5:^2{}".format(p, r))
                    self.msg("^7, ".join(f_msg))

                clients = len(teams["spectator"])
                if clients:
                    s_players = []
                    s_msg = []
                    for p in teams["spectator"]:
                        s_players.append([self.get_bdm_field(p, game_type, "rating"), re.sub(r"\^[0-9]", "", p.name)])
                    s_players = sorted(s_players, reverse=True)
                    for r, p in s_players:
                        s_msg.append("^7{}^5:^3{}".format(p, r))
                    self.msg("^7, ".join(s_msg))

            else:
                self.msg("^7The current ^2{} ^7game type does not have player bdm ratings.".format(self._bdm_gtype))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM get_bdms Exception: {}".format([e]))

    def teams_cmd(self, player, msg, channel):
        if bool(int(minqlx.get_cvar("qlx_bdmRespondToTeamsCommand"))):
            self.exec_bteams_cmd()
        else:
            self._agreeing_players = None
            self._players_agree = [False, False]
            self._suggested_switch = 0

    def bteams_cmd(self, player, msg, channel):
        self.exec_bteams_cmd()
        return

    @minqlx.thread
    def exec_bteams_cmd(self):
        try:
            if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                teams = self.teams()
                red_clients = len(teams["red"])
                blue_clients = len(teams["blue"])
                uneven_teams = False
                if red_clients == 0 and blue_clients == 0:
                    self.msg("^3The teams are empty of players.")
                    return
                elif red_clients != blue_clients:
                    self.msg("^1The teams do not have the same number of players !!!")
                    uneven_teams = True

                suggestion = self.suggest_switch(teams)
                message = ["^7Team Balance: ^1{} ^7vs. ^4{}".format(round(suggestion[4]), round(suggestion[5]))]
                if suggestion[2] > 0:
                    message.append(" ^7- Difference: ^1{}".format(suggestion[2]))
                elif suggestion[2] < 0:
                    message.append(" ^7- Difference: ^4{}".format(abs(suggestion[2])))
                else:
                    message.append(" ^7- ^2EVEN")
                self.msg("".join(message))

                if uneven_teams:
                    self.msg("^3A switch recommendation is not possible with uneven teams.")
                    self.clear_suggestion()
                    return

                if abs(suggestion[3]) < abs(suggestion[2]) and\
                        abs(suggestion[2]) >= int(minqlx.get_cvar("qlx_bdmMinimumSuggestionDiff")):
                    if not self.same_suggested_players(suggestion[0].id, suggestion[1].id):
                        self._agreeing_players = (suggestion[0].id, suggestion[1].id)
                        self._players_agree = [False, False]
                    self._suggested_switch = 1
                    self.msg("^6Switch ^1::^7{}^1::^7<-> ^4::^7{}^4:: ^6{}a ^7to agree."
                             .format(suggestion[0].name, suggestion[1].name, minqlx.get_cvar("qlx_commandPrefix")))
                    diff = int(minqlx.get_configstring(6)) - int(minqlx.get_configstring(7))
                    if suggestion[2] > 0 and diff < -2 or suggestion[2] < 0 and diff > 2:
                        self.msg("^3Team scores MAY not support this player switch")
                else:
                    self.msg("^6Teams look good.")
                    self.clear_suggestion()
            else:
                self.msg("^7This game type is not a supported Team-Based BDM game type.")
                self.clear_suggestion()
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM bteams_cmd Exception: {}".format([e]))

    def same_suggested_players(self, p1_id, p2_id):
        match = False
        try:
            if self._agreeing_players[0] == p1_id and self._agreeing_players[1] == p2_id:
                match = True
            elif self._agreeing_players[0] == p2_id and self._agreeing_players[1] == p1_id:
                match = True
        except:
            pass
        return match

    def cmd_mark_agree(self, player=None, msg=None, channel=None):
        try:
            if self._agreeing_players and self._agreeing_players[0] and \
                    self._agreeing_players[1] and self._suggested_switch == 1:
                self._players_agree[0] = True
                self._players_agree[1] = True
                if self.game.state in ["in_progress", "countdown"]:
                    if self._bdm_gtype in ROUND_BASED_GAMETYPES:
                        if not self._between_rounds or\
                                (self._start_countdown and
                                 self._countdown_time - (time.time() - self._start_countdown) < 1):
                            self.msg("^3The players will be switched after this round is complete.")
                            return
                    elif self._bdm_gtype in NO_COUNTDOWN_GAMESTYPES:
                        self.msg("^1Agreeing players will be switched in 10 seconds regardless of current actions.")

                        @minqlx.delay(10)
                        def switch_agreeing_players():
                            self.execute_switch()

                        switch_agreeing_players()
                        return
                self.execute_switch()
            elif self._suggested_switch == -1:
                self.msg("^3Teams makup has changed. Run {}{} again."
                         .format(minqlx.get_cvar("qlx_commandPrefix"),
                                 "teams" if bool(int(minqlx.get_cvar("qlx_bdmRespondToTeamsCommand"))) else "bteams"))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM cmd_mark_agree Exception: {}".format([e]))

    def cmd_bdmagree(self, player, msg, channel):
        try:
            if self._bdm_gtype not in TEAM_BASED_GAMETYPES or self._suggested_switch == 0:
                return
            if self._suggested_switch == -1:
                self.msg("^6Team makeups have changed. Run ^1{0}{1} ^6again."
                         .format(minqlx.get_cvar("qlx_commandPrefix"),
                                 "teams" if bool(int(minqlx.get_cvar("qlx_bdmRespondToTeamsCommand"))) else "bteams"))
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
                    if self.game.state in ["in_progress", "countdown"]:
                        if self._bdm_gtype in ROUND_BASED_GAMETYPES:
                            if not self._between_rounds or\
                                    (self._start_countdown and
                                     self._countdown_time - (time.time() - self._start_countdown) < 1):
                                self.msg("^3The players will be switched after this round is complete.")
                                return
                        elif self._bdm_gtype in NO_COUNTDOWN_GAMESTYPES:
                            if bool(int(minqlx.get_cvar("qlx_bdmRequireDoVote"))) and\
                                    bool(int(minqlx.get_cvar("qlx_bdmEnableDoVote"))):
                                self.msg("^3Both players have agreed. To perform the suggested switch a"
                                         " ^1/callvote do ^3is required.")
                                return
                            self.msg("^1Agreeing players will be switched in 10 seconds regardless of current actions.")

                            @minqlx.delay(10)
                            def switch_agreeing_players():
                                self.execute_switch()
                            switch_agreeing_players()
                            return
                    # Otherwise, switch right away.
                    self.execute_switch()
                else:
                    if not self._players_agree[0] and not self._players_agree[1]:
                        self.msg("^3Player ^6{} ^7and ^6{} ^7still need to ^2agree ^7to the switch."
                                 .format(player1, player2))
                    else:
                        self.msg("^3Player ^6{} ^7still needs to ^2agree ^7to the switch."
                                 .format(player1 if not self._players_agree[0] else player2))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM cmd_bdmagree Exception: {}".format([e]))

    def cmd_bdmversion(self, player, msg, channel):
        channel.reply("^7This server is running serverBDM.py ^2{0} version {1} by BarelyMiSSeD\n"
                      "https://github.com/BarelyMiSSeD/minqlx-plugins".format(self.__class__.__name__, VERSION))

    def cmd_bdmdo(self, player, msg, channel):
        try:
            """Forces a suggested switch to be done."""
            if self._agreeing_players and self._suggested_switch == 1:
                self.msg("^1Team switch recommendation is being forced by admin or do vote")
                self.execute_switch()
            elif len(msg) > 1:
                if self._agreeing_players and self._suggested_switch == -1 and msg[1] == "force":
                    self.msg("^1Team switch recommendation is being forced by admin")
                    self.execute_switch()
                else:
                    player.tell("^6Use ^1{}do force ^6to execute the switch even though team makeup has changed."
                                .format(minqlx.get_cvar("qlx_commandPrefix")))
            elif self._agreeing_players and self._suggested_switch == -1:
                player.tell("^6Use ^1{}do force ^6to execute the switch even though team makeup has changed."
                            .format(minqlx.get_cvar("qlx_commandPrefix")))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM cmd_bdmdo Exception: {}".format([e]))

    # Executes the player movement on the next game frame (player id, target team)
    @minqlx.next_frame
    def place_player(self, player_id, team):
        try:
            minqlx.console_command("put {} {}".format(player_id, team))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM place_player Exception: {}".format([e]))

    def balance_cmd(self, player, msg, channel):
        if bool(int(minqlx.get_cvar("qlx_bdmRespondToBalanceCommand"))):
            self.cmd_bdmbalance(player, msg, channel)

    # executes the balance command and the auto balance that happens during the round countdown.
    def cmd_bdmbalance(self, player=None, msg=None, channel=None):
        if self._locked[0] or self._locked[1] or time.time() - self._balance_time < 5:
            return
        if self._balance_time and time.time() - self._balance_time > 5:
            self._balance_time = 0
        self.exec_bdmbalance(pause=0.2 if player else 3)

    # Organizes players into teams from the highest to lowest BDM, then performs a balance.
    @minqlx.thread
    def exec_bdmbalance(self, pause):
        if self._balance_time:
            return
        for player in self.players():
            try:
                player.update()
            except:
                continue
        self._balance_time = time.time()
        time.sleep(pause)
        self.clear_suggestion()
        if self._bdm_gtype not in BDM_GAMETYPES:
            if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                self.msg("^3This is not a team based game type with bdm ratings.")
            else:
                self.msg("^3This is not a game type supported by this balance function.")
            self._balance_time = 0
            return
        self.clear_suggestion()
        teams = self.teams().copy()
        if len(teams["red"] + teams["blue"]) < 4:
            self.msg("^3There are not enough players on the teams to perform a balance.")
            return
        try:
            # Locks the teams if qlx_bdmLockTeamsForBalance is enabled
            if bool(int(minqlx.get_cvar("qlx_bdmLockTeamsForBalance"))):
                if ENABLE_LOG:
                    self.bdm_log.info("Locking teams to perform BDM balance.")
                minqlx.console_command("lock red")
                self._locked[0] = True
                minqlx.console_command("lock blue")
                self._locked[1] = True
                # Timer to unlock teams if this process get interrupted for any reason
                Timer(4, self.unlock_teams).start()
            exclude = None
            factory = minqlx.get_cvar("g_factory").lower()
            if factory == "ictf":
                game_type = "ictf"
            elif factory == "wipeout":
                game_type = "wipeout"
            else:
                game_type = self._bdm_gtype
            if (len(teams["red"]) + len(teams["blue"])) % 2 != 0:
                if bool(int(minqlx.get_cvar("qlx_bdmBalanceUnevenTeams"))):
                    try:
                        exclude = self.plugins["specqueue"].return_spec_player((teams["red"] + teams["blue"]))[0]
                    except KeyError:
                        lowest = int(minqlx.get_cvar("qlx_bdmMaxRating"))
                        for player in (teams["red"] + teams["blue"]):
                            bdm = self.get_bdm_field(player, game_type, "rating")
                            if bdm < lowest:
                                lowest = bdm
                                exclude = player
                    except Exception as e:
                        if ENABLE_LOG:
                            self.bdm_log.info("serverBDM exclude player {} Exception: {}".format(exclude, e))
                    if exclude:
                        if exclude in teams["red"]:
                            teams["red"].remove(exclude)
                        elif exclude in teams["blue"]:
                            teams["blue"].remove(exclude)
                else:
                    self.msg("^3The teams can't be made even. Balancing can't occur.")
                    return
            # If we have an even number of players but the teams are not even, make them even
            red_number = len(teams["red"])
            blue_number = len(teams["blue"])
            while red_number != blue_number:
                if red_number > blue_number:
                    teams["blue"].append(teams["red"].pop())
                    red_number -= 1
                    blue_number += 1
                else:
                    teams["red"].append(teams["blue"].pop())
                    blue_number -= 1
                    red_number += 1
            # Put all players into a sorted dictionary (sorted by player bdm)
            player_bdms = []
            player_info = {}
            for p in (teams["red"] + teams["blue"]):
                player_bdms.append([self.get_bdm_field(p, game_type, "rating"), p.steam_id])
                player_info[p.steam_id] = p
            sorted_bdms = sorted(player_bdms, reverse=True)
            # Put players into red and blue teams starting with the highest bdm players and alternate red and blue team
            player_count = 0
            teams = {"red": [], "blue": []}
            placement = ["red", "blue"]
            random.shuffle(placement)
            for k, v in sorted_bdms:
                p = player_info[v]
                if player_count % 2 == 0:
                    teams[placement[0]].append(p)
                else:
                    teams[placement[1]].append(p)
                player_count += 1
            # Start shuffling by looping through our suggestion function until
            # there are no more switches that can be done to improve teams.
            switch = self.suggest_switch(teams)
            while switch[0] and switch[1]:
                if switch[0] in teams["red"]:
                    teams["blue"].append(switch[0])
                    teams["red"].remove(switch[0])
                    teams["red"].append(switch[1])
                    teams["blue"].remove(switch[1])
                else:
                    teams["red"].append(switch[0])
                    teams["blue"].remove(switch[0])
                    teams["blue"].append(switch[1])
                    teams["red"].remove(switch[1])
                switch_temp = self.suggest_switch(teams)
                if switch[0] in switch_temp and switch[1] in switch_temp:
                    switch = [None, None]
                else:
                    switch = switch_temp
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
            curr_teams = self.teams().copy()
            for number in range(red_number):
                if teams["red"][number].steam_id in curr_teams["blue"]:
                    self.place_player(teams["red"][number].id, "red")
                if teams["blue"][number].steam_id in curr_teams["red"]:
                    self.place_player(teams["blue"][number].id, "blue")
            if exclude:
                if avg_blue > avg_red:
                    if exclude in curr_teams["blue"]:
                        self.place_player(exclude.id, "red")
                else:
                    if exclude in curr_teams["red"]:
                        self.place_player(exclude.id, "blue")
                self.msg("^6{} ^4was not included in the balance.".format(exclude))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM exec_bdmbalance Exception: {}".format([e]))

        if self._locked[0] or self._locked[1]:
            time.sleep(0.3)
            if ENABLE_LOG:
                self.bdm_log.info("Unlocking teams after balance execution.")
            minqlx.console_command("unlock red")
            self._locked[0] = False
            minqlx.console_command("unlock blue")
            self._locked[1] = False
        time.sleep(0.5)
        self._balance_time = 0

    # Executes the auto balance at the start of the game countdown. This requires the teams to be locked.
    def cd_bdmbalance(self, player=None, msg=None, channel=None):
        if self._locked[0] or self._locked[1] or time.time() - self._balance_time < 5:
            return
        if self._balance_time and time.time() - self._balance_time > 5:
            self._balance_time = 0
        self.exec_cd_bdmbalance()

    # Performs the balance differently than above. This requires the teams to be locked and player switches to happen.
    #   The more thorough balancing done above is not possible before the game begins because it may make the server
    #     stop the countdown to the game due to the team changes.
    @minqlx.thread
    def exec_cd_bdmbalance(self):
        if self._balance_time:
            return
        for player in self.players():
            try:
                player.update()
            except:
                continue
        self._balance_time = time.time()
        time.sleep(0.2)
        self.clear_suggestion()
        if self._bdm_gtype not in BDM_GAMETYPES:
            if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                self.msg("^3This is not a team based game type with bdm ratings.")
            else:
                self.msg("^3This is not a game type supported by this balance function.")
            self._balance_time = 0
            return
        teams = self.teams()
        if len(teams["red"] + teams["blue"]) < 4:
            self.msg("^3There are not enough players on the teams to perform a balance.")
            return
        try:
            if ENABLE_LOG:
                self.bdm_log.info("Locking teams to perform pre-game auto BDM balance.")
            minqlx.console_command("lock red")
            self._locked[0] = True
            minqlx.console_command("lock blue")
            self._locked[1] = True
            # Timer to unlock teams if this process gets uncontrollably interrupted for any reason
            Timer(4, self.unlock_teams).start()
            exclude = None
            factory = minqlx.get_cvar("g_factory").lower()
            if factory == "ictf":
                game_type = "ictf"
            elif factory == "wipeout":
                game_type = "wipeout"
            else:
                game_type = self._bdm_gtype
            teams = self.teams().copy()
            if len(teams["red"] + teams["blue"]) % 2 != 0:
                if bool(int(minqlx.get_cvar("qlx_bdmBalanceUnevenTeams"))):
                    try:
                        exclude = self.plugins["specqueue"].return_spec_player((teams["red"] + teams["blue"]))[0]
                    except KeyError:
                        lowest = int(minqlx.get_cvar("qlx_bdmMaxRating"))
                        for player in (teams["red"] + teams["blue"]):
                            bdm = self.get_bdm_field(player, game_type, "rating")
                            if bdm < lowest:
                                lowest = bdm
                                exclude = player
                    except Exception as e:
                        if ENABLE_LOG:
                            self.bdm_log.info("serverBDM exec_cd_bdmbalance exclude player {} Exception: {}"
                                              .format(exclude, e))
                    if exclude:
                        if exclude in teams["red"]:
                            teams["red"].remove(exclude)
                        elif exclude in teams["blue"]:
                            teams["blue"].remove(exclude)
                else:
                    self.msg("^3The teams are not even. Balancing can't occur.")
                    minqlx.console_command("unlock red")
                    self._locked[0] = False
                    minqlx.console_command("unlock blue")
                    self._locked[1] = False
                    self._balance_time = 0
                    return
            # If we have an even number of players but the teams are not even, make them even
            red_number = len(teams["red"])
            blue_number = len(teams["blue"])
            while red_number != blue_number:
                if red_number > blue_number:
                    move_player = teams["red"].pop()
                    self.place_player(move_player.id, "blue")
                    teams["blue"].append(move_player)
                    red_number -= 1
                    blue_number += 1
                else:
                    move_player = teams["blue"].pop()
                    self.place_player(move_player.id, "red")
                    teams["red"].append(move_player)
                    blue_number -= 1
                    red_number += 1
            # Start shuffling by looping through our suggestion function until
            # there are no more switches that can be done to improve teams.
            player_switch = self.suggest_switch(teams)
            while player_switch[0] and player_switch[1]:
                if player_switch[0] in teams["red"]:
                    self.place_player(player_switch[0].id, "blue")
                    self.place_player(player_switch[1].id, "red")
                    teams["blue"].append(player_switch[0])
                    teams["red"].remove(player_switch[0])
                    teams["red"].append(player_switch[1])
                    teams["blue"].remove(player_switch[1])
                else:
                    self.place_player(player_switch[0].id, "red")
                    self.place_player(player_switch[1].id, "blue")
                    teams["red"].append(player_switch[0])
                    teams["blue"].remove(player_switch[0])
                    teams["blue"].append(player_switch[1])
                    teams["red"].remove(player_switch[1])
                switch_temp = self.suggest_switch(teams)
                if player_switch[0] in switch_temp and player_switch[1] in switch_temp:
                    player_switch = [None, None]
                else:
                    player_switch = switch_temp
            time.sleep(1)

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

            if exclude:
                if avg_blue > avg_red:
                    if exclude in self.teams()["blue"]:
                        self.place_player(exclude.id, "red")
                else:
                    if exclude in self.teams()["red"]:
                        self.place_player(exclude.id, "blue")
                self.msg("^6{} ^4was not included in the balance.".format(exclude))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM Game Countdown Balance Exception: {}".format([e]))
        if ENABLE_LOG:
            self.bdm_log.info("Unlocking teams after pre-game auto balance execution.")
        minqlx.console_command("unlock red")
        self._locked[0] = False
        minqlx.console_command("unlock blue")
        self._locked[1] = False
        time.sleep(0.5)
        self._balance_time = 0

    def cmd_damage_status(self, player=None, msg=None, channel=None):
        self.exec_damage_status(player, msg, channel)

    @minqlx.thread
    def exec_damage_status(self, player=None, msg=None, channel=None):
        try:
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
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM exec_damage_status Exception: {}".format([e]))

    def cmd_dmg_status(self, player=None, msg=None, channel=None):
        try:
            teams = self.teams()
            if self.game.state not in ["in_progress", "countdown"]:
                self.msg("^3Match is not in progress")
            if len(msg) > 1:
                try:
                    pid = int(msg[1])
                    p = self.player(pid)
                except minqlx.NonexistentPlayerError:
                    self.msg("^1Invalid player ID.")
                    return
                except ValueError:
                    p, pid = self.find_player(" ".join(msg[1:]))
                    if pid == -1:
                        if p == 0:
                            player.tell("^1Too Many players matched your player name")
                        else:
                            player.tell("^1No player matching that name found")
                        return minqlx.RET_STOP_ALL
                player = p
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
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM cmd_dmg_status Exception: {}".format([e]))

    def cmd_game_status(self, player=None, msg=None, channel=None):
        self.exec_game_status()

    @minqlx.thread
    def exec_game_status(self):
        try:
            minqlx.console_print("^6Game Status: ^4Map ^1- ^7{} ^5Game Mode ^1- ^7{}"
                                 .format(minqlx.get_cvar("mapname"), self._bdm_gtype.upper()))
            teams = self.teams()
            if len(teams["red"] + teams["blue"] + teams["free"] + teams["spectator"]) == 0:
                minqlx.console_print("^3No players connected")
            else:
                if self.game.state not in ["in_progress", "countdown"]:
                    minqlx.console_print("^3Match is not in progress")
                if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                    red_team = []
                    blue_team = []
                    minqlx.console_print("^1RED^7: ^7{} ^6::: ^4BLUE^7: {}"
                                         .format(minqlx.get_configstring(6), minqlx.get_configstring(7)))
                    for player in teams["red"]:
                        red_team.append("    ^1{} ^5{} ^6{} ^7{} {} ^2{}^7/^1{} ^2{}^7/^1{}"
                                        .format(player.id, player.stats.ping, player.stats.score, player,
                                                "^7(^2ALIVE^7)" if player.is_alive else "^7(^1DEAD^7)",
                                                player.stats.kills, player.stats.deaths, player.stats.damage_dealt,
                                                player.stats.damage_taken))
                    minqlx.console_print("^1Red^7: ^7(^1ID ^5Ping ^6Score ^7Name ^2Kills^7/^1Deaths"
                                         " ^2DmgDlt^7/^1DmgTkn^7) ^1{} ^7Players".format(len(red_team)))
                    for player in red_team:
                        minqlx.console_print(player)
                    for player in teams["blue"]:
                        blue_team.append("    ^4{} ^5{} ^6{} ^7{} {} ^2{}^7/^1{} ^2{}^7/^1{}"
                                         .format(player.id, player.stats.ping, player.stats.score, player,
                                                 "^7(^2ALIVE^7)" if player.is_alive else "^7(^1DEAD^7)",
                                                 player.stats.kills, player.stats.deaths, player.stats.damage_dealt,
                                                 player.stats.damage_taken))
                    minqlx.console_print("^4Blue^7: ^7(^4ID ^5Ping ^6Score ^7Name ^2Kills^7/^1Deaths"
                                         " ^2DmgDlt^7/^1DmgTkn^7) ^4{} ^7Players".format(len(blue_team)))
                    for player in blue_team:
                        minqlx.console_print(player)
                else:
                    for player in teams["free"]:
                        minqlx.console_print("{}^7: {} ^6Ping^7: {}"
                                             .format(player, player.stats.score, player.stats.ping))

                try:
                    specq = self.plugins["specqueue"]
                except KeyError:
                    specq = None
                for player in teams["spectator"]:
                    if specq:
                        queue = specq.player_in_queue(player.steam_id)
                        slot = queue + 1 if queue is not None else None
                    else:
                        slot = False
                    minqlx.console_print("^6Spectator^7: {} {} {}"
                                         .format(player.id, player,
                                                 "^7(^2Queue Pos: {}^7)".format(slot) if slot else ""))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM exec_game_status Exception: {}".format([e]))

    # ==============================================
    #               Script Commands
    # ==============================================
    # If serverBDM should respond to the teams and/or the balance command, this will remove those
    # commands if they exist in other plugins
    @minqlx.delay(3)
    def remove_conflicting_commands(self):
        teams = bool(int(minqlx.get_cvar("qlx_bdmRespondToTeamsCommand")))
        balance = bool(int(minqlx.get_cvar("qlx_bdmRespondToBalanceCommand")))
        elo = int(minqlx.get_cvar("qlx_bdmModifyEloCmds"))
        loaded_scripts = self.plugins
        loaded_scripts.pop(self.__class__.__name__)
        if elo in [1, 2] and "balance" in loaded_scripts:
            minqlx.unload_plugin("balance")
            loaded_scripts.pop("balance")
            minqlx.console_print("^1serverBDM: Unloading the ^7balance ^1plugin")
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM: Unloading the balance plugin")
        for script, handler in loaded_scripts.items():
            try:
                for cmd in handler.commands:
                    if (teams and {"teams", "a", "do"}.intersection(cmd.name)) or \
                            (balance and {"balance"}.intersection(cmd.name)) or \
                            (elo == 1 and {"elo", "elos"}.intersection(cmd.name)):
                        handler.remove_command(cmd.name, cmd.handler)
                        minqlx.console_print("^1serverBDM: Removing command ^7{} ^1used in ^7{} ^1plugin"
                                             .format(cmd.name, script))
                        if ENABLE_LOG:
                            self.bdm_log.info("serverBDM: Removing command {} used in {} plugin"
                                              .format(cmd.name, script))
            except Exception as e:
                if ENABLE_LOG:
                    self.bdm_log.info("serverBDM remove_conflicting_commands Exception: {}".format([e]))
                continue

    # Displays the join message for the supplied player
    def display_join_message(self, player):
        factory = minqlx.get_cvar("g_factory").lower()
        if factory == "ictf":
            game_type = "ictf"
        elif factory == "wipeout":
            game_type = "wipeout"
        else:
            game_type = self._bdm_gtype
        try:
            games_completed = int(self.get_db_field(player, "minqlx:players:{}:games_completed"))
        except TypeError:
            games_completed = 0
        except ValueError:
            games_completed = 0
        except Exception as e:
            games_completed = 0
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM Games Completed retrieval error: {}".format([e]))
        try:
            games_left = int(self.get_db_field(player, "minqlx:players:{}:games_left"))
        except TypeError:
            games_left = 0
        except ValueError:
            games_left = 0
        except Exception as e:
            games_left = 0
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM Games Left retrieval error: {}".format([e]))
        games_played = games_completed + games_left
        try:
            if games_completed > 0:
                quit_percentage = round((games_left / games_completed) * 100)
            else:
                quit_percentage = 0
        except Exception as e:
            quit_percentage = 0
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM Games Quit Percentage calculation error for {}^7: {}".format(player, e))
        try:
            bdm_rating = self.get_bdm_field(player, game_type, "rating")
        except Exception as e:
            bdm_rating = int(minqlx.get_cvar("qlx_bdmDefaultBDM"))
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM BDM Rating retrieval error: {}".format([e]))
        try:
            bdm_completed = self.get_bdm_field(player, game_type, "games_completed")
        except Exception as e:
            bdm_completed = 0
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM BDM Completed retrieval error: {}".format([e]))
        try:
            bdm_left = self.get_bdm_field(player, game_type, "games_left")
        except Exception as e:
            bdm_left = 0
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM BDM Left retrieval error: {}".format([e]))
        bdm_total = bdm_completed + bdm_left
        try:
            if bdm_completed != 0:
                bdm_quit_percentage = round(bdm_left / bdm_completed * 100)
            else:
                bdm_quit_percentage = 0
        except Exception as e:
            bdm_quit_percentage = 0
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM Quit calculation error: {}".format([e]))
        join_msg = minqlx.get_cvar("qlx_bdmJoinMessage").replace("%", "％")
        try:
            self.msg(join_msg.format(player, bdm_rating, bdm_completed, bdm_left, bdm_total,
                                     bdm_quit_percentage, games_played, games_completed, games_left,
                                     quit_percentage))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM Print Join Message error: {}".format([e]))

    # executes team unlock commands ... to ensure teams are unlocked after balance execution
    def unlock_teams(self):
        try:
            if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                minqlx.console_command("unlock red")
                minqlx.console_command("unlock blue")
            else:
                minqlx.console_command("unlock free")
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM unlock_teams Exception: {}".format([e]))

    # Search for a player name match using the supplied string
    def find_player(self, name):
        try:
            found_player = None
            found_count = 0
            # Remove color codes from the supplied string
            player_name = re.sub(r"\^[0-9]", "", name).lower()
            # search through the list of connected players for a name match
            for player in self.players():
                if player_name in re.sub(r"\^[0-9]", "", player.name).lower():
                    # if match is found return player, player id
                    found_player = player
                    found_count += 1
            # if only one match was found return player, player id
            if found_count == 1:
                return found_player, int(str([found_player]).split(":")[0].split("(")[1])
            # if more than one match is found return 0, -1
            elif found_count > 1:
                return 0, -1
            # if no match is found return -1, -1
            else:
                return -1, -1
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM find_player Exception: {}".format([e]))

    @minqlx.thread
    def check_force_switch_vote(self, caller, vote):
        try:
            self.callvote("qlx {}mark_agree".format(minqlx.get_cvar("qlx_commandPrefix")),
                          "Force the suggested player switch?")
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called vote /cv {}".format(caller.name, vote))
            voter_perc = int(minqlx.get_cvar("qlx_bdmPlayerPercForVote"))
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
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM check_force_switch_vote Exception: {}".format([e]))

    def check_entry_exists(self, player, game_type, field):
        try:
            return self.db.exists(BDM_KEY.format(player.steam_id, game_type, field))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM check_entry_exists Exception: {}".format([e]))

    def get_bdm_field(self, player, game_type, field):
        try:
            if self.db.exists(BDM_KEY.format(player.steam_id, game_type, field)):
                value = self.db.get(BDM_KEY.format(player.steam_id, game_type, field))
            else:
                if field == "rating":
                    value = self.default_bdm(player)
                else:
                    value = 0
            try:
                data = int(value)
            except ValueError:
                split_rating = value.split(".")
                data = int(split_rating[0])
            return data
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM get_bdm_field Exception: {}".format([e]))

    def get_db_field(self, player, field):
        try:
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
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM get_db_field Exception: {}".format([e]))

    def set_bdm_field(self, player, game_type, field, data, overwrite=True):
        try:
            if overwrite:
                self.db.set(BDM_KEY.format(player.steam_id, game_type, field), str(data))
            else:
                self.db.setnx(BDM_KEY.format(player.steam_id, game_type, field), str(data))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM set_bdm_field Exception: {}".format([e]))

    def record_ctf_events(self, sid, medal):
        try:
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
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM record_ctf_events Exception: {}".format([e]))

    def record_ft_events(self, stats):
        try:
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
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM record_ft_events Exception: {}".format([e]))

    def player_disconnect_record(self, player):
        try:
            sid = str(player[0].steam_id)
            if sid[0] == "9":
                return
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
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM player_disconnect_record Exception: {}".format([e]))

    @minqlx.next_frame
    def team_switch_record(self, player, new_team, old_team):
        try:
            sid = str(player.steam_id)
            if sid[0] == "9":
                return
            if sid not in self._played_time:
                self.init_played_time(sid)
            if self._bdm_gtype in TEAM_BASED_GAMETYPES:
                if self.game.state != "in_progress":
                    return
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
                        self._played_time[sid]["team"] = new_team
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
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM team_switch_record Exception: {}".format([e]))

    def init_played_time(self, sid):
        try:
            self._played_time[sid] = {}
            self._played_time[sid]["team"] = ""
            self._played_time[sid]["score"] = 0
            self._played_time[sid]["kills"] = 0
            self._played_time[sid]["deaths"] = 0
            self._played_time[sid]["damage_dealt"] = 0
            self._played_time[sid]["damage_taken"] = 0
            self._played_time[sid]["time"] = 0
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM init_played_time Exception: {}".format([e]))

    def reset_data(self):
        try:
            self._played_time.clear()
            self._disconnected_players.clear()
            self._team_switchers.clear()
            self._spectating_players.clear()
            self._match_stats.clear()
            self._player_stats.clear()
            self._record_events.clear()
            self.game_active = False
            self.rounds_played = 0
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM reset data Exception: {}".format([e]))

    def default_bdm(self, player):
        try:
            if str(player.steam_id)[0] == "9":
                player_bdm = int(900 + 900 * (float(player.cvars["skill"].strip()) / 10))
            else:
                player_bdm = int(minqlx.get_cvar("qlx_bdmDefaultBDM"))
            return player_bdm
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM default_bdm Exception: {}".format([e]))

    def suggest_switch(self, teams):
        try:
            factory = minqlx.get_cvar("g_factory").lower()
            if factory == "ictf":
                game_type = "ictf"
            elif factory == "wipeout":
                game_type = "wipeout"
            else:
                game_type = self._bdm_gtype
            red_clients = len(teams["red"])
            blue_clients = len(teams["blue"])
            red_team_bdm = {}
            blue_team_bdm = {}
            red_bdm = 0
            blue_bdm = 0
            for client in teams["red"]:
                rating = self.get_bdm_field(client, game_type, "rating")
                red_bdm += rating
                red_team_bdm[client.steam_id] = rating
            red_bdm /= red_clients
            for client in teams["blue"]:
                rating = self.get_bdm_field(client, game_type, "rating")
                blue_bdm += rating
                blue_team_bdm[client.steam_id] = rating
            blue_bdm /= blue_clients
            player1 = None
            player2 = None
            difference = round(red_bdm) - round(blue_bdm)
            diff = 99999
            new_difference = 99999
            if abs(difference) > 0:
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
                try:
                    if abs(new_difference) < abs(difference):
                        player1 = self.player(players[0])
                        player2 = self.player(players[1])
                except Exception as e:
                    if ENABLE_LOG:
                        self.bdm_log.info("serverBDM suggest_switch Exception: {}".format([e]))
            return [player1, player2, difference, new_difference, red_bdm, blue_bdm]
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM suggest_switch Exception: {}".format([e]))

    def team_average(self, team):
        try:
            """Calculates the average rating of a team."""
            avg = 0
            factory = minqlx.get_cvar("g_factory").lower()
            if factory == "ictf":
                game_type = "ictf"
            elif factory == "wipeout":
                game_type = "wipeout"
            else:
                game_type = self._bdm_gtype
            if team:
                for p in team:
                    rating = self.get_bdm_field(p, game_type, "rating")
                    avg += int(rating)
                avg /= len(team)
            return round(avg)
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM team_average Exception: {}".format([e]))

    def clear_suggestion(self):
        try:
            self._agreeing_players = None
            self._players_agree = [False, False]
            self._suggested_switch = 0
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM clear_suggestion Exception: {}".format([e]))

    @minqlx.thread
    def execute_switch(self, delay=False):
        try:
            if delay:
                time.sleep(3)
            if not bool(int(minqlx.get_cvar("qlx_bdmEnableSwitch"))):
                self.msg("^4This script is still collecting data.")
                self.msg("^4The server admin will enable this switch function when enough data has been collected.")
                return
            self._players_agree = [False, False]
            self._suggested_switch = 0
            if self._agreeing_players:
                player1 = self.player(int(self._agreeing_players[0]))
                player2 = self.player(int(self._agreeing_players[1]))
                try:
                    player1.update()
                    player2.update()
                except Exception as e:
                    if ENABLE_LOG:
                        self.bdm_log.info("serverBDM execute_switch player update Exception: {}".format([e]))
                    return
                teams = self.teams()
                if player1 in teams["red"] and player2 in teams["blue"]:
                    self.place_player(player1.id, "blue")
                    self.place_player(player2.id, "red")
            self._agreeing_players = None
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM execute_switch Exception: {}".format([e]))

    @minqlx.thread
    def round_stats_record(self):
        try:
            teams = self.teams()
            for player in teams["red"] + teams["blue"]:
                sid = str(player.steam_id)
                if sid[0] == "9":
                    continue
                if sid not in self._played_time:
                    self._played_time[sid] = {}
                    self._played_time[sid]["team"] = ""
                stats = player.stats
                self._played_time[sid]["score"] = stats.score
                self._played_time[sid]["kills"] = stats.kills
                self._played_time[sid]["deaths"] = stats.deaths
                self._played_time[sid]["damage_dealt"] = stats.damage_dealt
                self._played_time[sid]["damage_taken"] = stats.damage_taken
                self._played_time[sid]["time"] = stats.time
            return True
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM round_stats_record Exception: {}".format([e]))
            return False

    @minqlx.thread
    def players_in_teams(self):
        try:
            time.sleep(2)
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
                        if sid not in self._played_time:
                            self.init_played_time(sid)
                        self._played_time[sid]["team"] = "red"
                    for player in teams["blue"]:
                        sid = str(player.steam_id)
                        if sid[0] == "9":
                            continue
                        if sid not in self._played_time:
                            self.init_played_time(sid)
                        self._played_time[sid]["team"] = "blue"
                else:
                    for player in teams["free"]:
                        sid = str(player.steam_id)
                        if sid[0] == "9":
                            continue
                        if sid not in self._played_time:
                            self.init_played_time(sid)
                        self._played_time[sid]["team"] = "free"
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM players_in_teams Exception: {}".format([e]))

    # noinspection PyMethodMayBeStatic
    def check_dict_value_greater(self, dic, sid, key, check_against):
        try:
            return dic[sid][key] > check_against
        except KeyError:
            return False

    def process_game_data(self, num, id, o, n, game_type, game_time):
        try:
            match_time = 0
            self.game_active = False
            self._save_previous_bdm = {}
            self._player_stats = {}
            self._match_stats = {}
            self._player_stats["DmgASum"] = 0
            self._player_stats["bdmSum"] = 0
            match_perc = int(minqlx.get_cvar("qlx_bdmMinTimePerc")) / 100.0
            if game_type in TEAM_BASED_GAMETYPES:
                self.player_count = 0
                if game_type in ROUND_BASED_GAMETYPES:
                    if game_type == "wipeout":
                        min_rounds = int(minqlx.get_cvar("qlx_bdmWoMinRounds"))
                    else:
                        min_rounds = int(minqlx.get_cvar("qlx_bdmMinRounds"))
                    if self.rounds_played < min_rounds:
                        if ENABLE_LOG:
                            num.value = -1
                            self.bdm_log.info("--- Only {} rounds played but need {} rounds,"
                                              " BDM is not being calculated ---"
                                              .format(self.rounds_played, int(minqlx.get_cvar("qlx_bdmMinRounds"))))
                        return
                for sid, stats in self._end_game_players.items():
                    if not sid or not stats or str(sid)[0] == "9":
                        continue
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
                if game_type == "ca":
                    finished_calc = self.calc_ca_dmga(needed_time, match_time)
                elif game_type == "ft":
                    finished_calc = self.calc_ft_dmga(needed_time, match_time)
                elif game_type == "wipeout":
                    finished_calc = self.calc_wipeout_dmga(needed_time, match_time)
                elif game_type == "tdm":
                    finished_calc = self.calc_tdm_dmga(needed_time, match_time)
                elif game_type in ["ctf", "ictf"]:
                    finished_calc = self.calc_ctf_dmga(needed_time, match_time, game_type)
                if not finished_calc:
                    if ENABLE_LOG:
                        self.bdm_log.info("serverBDM Error calculating {} DmgA.".format(game_type))
                    return
                if self.player_count < (int(minqlx.get_cvar("qlx_bdmMinimumTeamSize")) * 2):
                    if ENABLE_LOG:
                        num.value = -2
                        self.bdm_log.info("--- There are only {} players on each team, {} are needed. "
                                          "BDM stats not being calculated ---"
                                          .format(int(round(self.player_count / 2)),
                                                  int(minqlx.get_cvar("qlx_bdmMinimumTeamSize"))))
                    return
            elif game_type in BDM_GAMETYPES:
                for sid, stats in self._end_game_players.items():
                    if str(sid)[0] == "9":
                        continue
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
                    if ENABLE_LOG:
                        self.bdm_log.info("serverBDM Error calculating {} DmgA.".format(game_type))
                    return
            # Calculate New BDMs based on DmgA calculations
            self.calc_new_bdm(game_type, num, id, o, n)
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM process_game Exception: {}".format([e]))

    def calc_ffa_dmga(self, needed_time, match_time):
        try:
            per_kill_pts = int(minqlx.get_cvar("qlx_bdmFfaKillPts"))
            for sid in self._disconnected_players:
                if self._disconnected_players[sid]["time"] >= needed_time:
                    self._player_stats[sid] = {}
                    self._player_stats[sid]["left_game"] = 1
                    self._player_stats[sid]["DmgA"] = ((self._disconnected_players[sid]["damage_dealt"] +
                                                        self._disconnected_players[sid]["kills"] * per_kill_pts) *
                                                       match_time / self._disconnected_players[sid]["time"])
                    self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, "ffa")

            for sid in self._match_stats:
                if self._match_stats[sid]["time"] >= needed_time:
                    self._player_stats[sid] = {}
                    self._player_stats[sid]["left_game"] = 0
                    self._player_stats[sid]["DmgA"] = ((self._match_stats[sid]["damage_dealt"] +
                                                        self._match_stats[sid]["kills"] * per_kill_pts) *
                                                       match_time / self._match_stats[sid]["time"])
                    self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, "ffa")
            return True
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM calc_ffa_dmga Exception: {}".format([e]))

    def calc_ca_dmga(self, needed_time, match_time):
        try:
            per_kill_pts = int(minqlx.get_cvar("qlx_bdmCaKillPts"))
            dmg_rcvd_perc = int(minqlx.get_cvar("qlx_bdmDamageRcvdPerc")) / 100.0
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
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, "ca")

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
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, "ca")

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
                        self._player_stats["bdmSum"] += self.sid_bdm(sid, "ca")
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
                        self._player_stats["bdmSum"] += self.sid_bdm(sid, "ca")

            return True
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM calc_ca_dmga Exception: {}".format([e]))

    def calc_wipeout_dmga(self, needed_time, match_time):
        try:
            per_kill_pts = int(minqlx.get_cvar("qlx_bdmWoKillPts"))
            per_death_pts = int(minqlx.get_cvar("qlx_bdmWoDeathPts"))
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
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, "wipeout")

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
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, "wipeout")

            for sid in self._match_stats:
                if sid in self._team_switchers:
                    play_time = self._match_stats[sid]["time"] + self._team_switchers[sid]["time"]
                    if play_time >= needed_time:
                        self.player_count += 1
                        damage_dealt = self._match_stats[sid]["damage_dealt"] + self._team_switchers[sid][
                            "damage_dealt"]
                        kills = self._match_stats[sid]["kills"] + self._team_switchers[sid]["kills"]
                        deaths = self._match_stats[sid]["deaths"] + self._team_switchers[sid]["deaths"]
                        self._player_stats[sid] = {}
                        self._player_stats[sid]["left_game"] = 0
                        self._player_stats[sid]["DmgA"] = ((damage_dealt + (kills * per_kill_pts) -
                                                            (deaths * per_death_pts)) * match_time / play_time)
                        self._player_stats["DmgASum"] += self._player_stats[sid]["DmgA"]
                        self._player_stats["bdmSum"] += self.sid_bdm(sid, "wipeout")
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
                        self._player_stats["bdmSum"] += self.sid_bdm(sid, "wipeout")
            return True
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM calc_wipeout_dmga Exception: {}".format([e]))

    def calc_ft_dmga(self, needed_time, match_time):
        try:
            per_kill_pts = int(minqlx.get_cvar("qlx_bdmFtKillPts"))
            per_thaw_pts = int(minqlx.get_cvar("qlx_bdmFtThawPts"))
            per_frozen_pts = int(minqlx.get_cvar("qlx_bdmFtFrozenPts"))
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
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, "ft")

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
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, "ft")

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
                        self._player_stats["bdmSum"] += self.sid_bdm(sid, "ft")
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
                        self._player_stats["bdmSum"] += self.sid_bdm(sid, "ft")
            return True
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM calc_ft_dmga Exception: {}".format([e]))

    def calc_ctf_dmga(self, needed_time, match_time, game_type):
        try:
            dmg_rcvd_perc = int(minqlx.get_cvar("qlx_bdmDamageRcvdPerc")) / 100.0
            if game_type == "ictf":
                per_kill_pts = int(minqlx.get_cvar("qlx_bdmICtfKillPts"))
                per_cap_pts = int(minqlx.get_cvar("qlx_bdmICtfCapPts"))
                per_assist_pts = int(minqlx.get_cvar("qlx_bdmICtfAssistPts"))
                per_defense_pts = int(minqlx.get_cvar("qlx_bdmICtfDefensePts"))
            else:
                per_kill_pts = int(minqlx.get_cvar("qlx_bdmCtfKillPts"))
                per_cap_pts = int(minqlx.get_cvar("qlx_bdmCtfCapPts"))
                per_assist_pts = int(minqlx.get_cvar("qlx_bdmCtfAssistPts"))
                per_defense_pts = int(minqlx.get_cvar("qlx_bdmCtfDefensePts"))

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
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, game_type)

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
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, game_type)

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
                        self._player_stats["bdmSum"] += self.sid_bdm(sid, game_type)
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
                        self._player_stats["bdmSum"] += self.sid_bdm(sid, game_type)
            return True
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM calc_ctf_dmga Exception: {}".format([e]))

    def calc_tdm_dmga(self, needed_time, match_time):
        try:
            per_kill_pts = int(minqlx.get_cvar("qlx_bdmTdmKillPts"))
            per_death_pts = int(minqlx.get_cvar("qlx_bdmTdmDeathPts"))
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
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, "tdm")

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
                    self._player_stats["bdmSum"] += self.sid_bdm(sid, "tdm")

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
                        self._player_stats["bdmSum"] += self.sid_bdm(sid, "tdm")
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
                        self._player_stats["bdmSum"] += self.sid_bdm(sid, "tdm")
            return True
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM calc_tdm_dmga Exception: {}".format([e]))

    def calc_new_bdm(self, game_type, num, sid, old, new):
        try:
            min_rating = int(minqlx.get_cvar("qlx_bdmMinRating"))
            max_rating = int(minqlx.get_cvar("qlx_bdmMaxRating"))
            print_change = bool(int(minqlx.get_cvar("qlx_bdmConsolePrintBdmChange")))
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
                max_games_for_calc = int(minqlx.get_cvar("qlx_bdmNumGamesForCalculation"))
                games_played = games if games < max_games_for_calc else max_games_for_calc
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
                name = self.player(int(p_sid)).name
                if not name:
                    name = self.db.lindex("minqlx:players:{}".format(p_sid), 0)
                if ENABLE_LOG:
                    self.bdm_log.info("Player: {} BDM Change: Old = {}, New = {}"
                                      .format(re.sub(r"\^[0-9]", "", name), rating, new_rating))
                if print_change:
                    sid[num.value] = p_sid
                    old[num.value] = rating
                    new[num.value] = new_rating
                    num.value += 1

            if len(self._save_previous_bdm) > 0:
                for player in self._save_previous_bdm:
                    for x in range(5, 1, -1):
                        if self.db.exists(BDM_KEY.format(player, game_type, "rating{}".format(x - 1))):
                            rating = self.db.get(BDM_KEY.format(player, game_type, "rating{}".format(x - 1)))
                            self.db.set(BDM_KEY.format(player, game_type, "rating{}".format(x)), rating)
                    self.db.set(BDM_KEY.format(player, game_type, "rating1"), self._save_previous_bdm[player])
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM calc_new_bdm Exception: {}".format([e]))

    def sid_bdm(self, player, game_type):
        try:
            if self.db.exists(BDM_KEY.format(player, game_type, "rating")):
                value = int(self.db.get(BDM_KEY.format(player, game_type, "rating")))
            else:
                if field == "rating":
                    value = self.default_bdm(self.player(player))
                else:
                    value = 0
            return value
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM sid_bdm Exception: {}".format([e]))

    def print_changes(self, n, sid, old, new):
        try:
            if n.value > 0:
                for x in range(n.value):
                    minqlx.console_print("Player: {} BDM Change: Old = {}, New = {}"
                                         .format(self.player(sid[x]), old[x], new[x]))
            elif n.value == -1:
                minqlx.console_print("^7--- ^6Only {} rounds played but need {} rounds,"
                                     " BDM is not being calculated ^7---"
                                     .format(self.rounds_played, int(minqlx.get_cvar("qlx_bdmMinRounds"))))
            elif n.value == -2:
                minqlx.console_print("^7--- ^6There were not enough players on each team, {} are needed. "
                                     "BDM stats not being calculated ^7---"
                                     .format(int(minqlx.get_cvar("qlx_bdmMinimumTeamSize"))))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM print_changes Exception: {}".format([e]))

    @minqlx.thread
    def set_initial_bdm(self, player, game_type):
        try:
            sid = player.steam_id
            if game_type == "wipeout":
                if self.db.exists(BDM_KEY.format(sid, "ca", "rating")):
                    rating = self.db.get(BDM_KEY.format(sid, "ca", "rating"))
                    self.db.set(BDM_KEY.format(sid, game_type, "rating"), str(rating))
                    return
                else:
                    game_type = "ca"
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
                    response = True
                    break
            if response:
                elo_dict[sid] = {}
                for record in info_js["players"]:
                    for gt in BDM_GAMETYPES:
                        if gt in record:
                            elo_dict[sid][gt] = record[str(gt)]["elo"]
                        else:
                            elo_dict[sid][gt] = 1200

                m = float(minqlx.get_cvar("qlx_bdmMCalculation"))
                b = float(minqlx.get_cvar("qlx_bdmBCalculation"))
                if game_type in elo_dict[sid]:
                    bdm = int(m * int(elo_dict[sid][game_type]) + b)
                else:
                    bdm = int(minqlx.get_cvar("qlx_bdmDefaultBDM"))
                if bdm < int(minqlx.get_cvar("qlx_bdmMinRating")):
                    bdm = int(minqlx.get_cvar("qlx_bdmMinRating"))
                elif bdm > int(minqlx.get_cvar("qlx_bdmMaxRating")):
                    bdm = int(minqlx.get_cvar("qlx_bdmMaxRating"))
                self.db.set(BDM_KEY.format(sid, game_type, "rating"), str(bdm))
        except Exception as e:
            if ENABLE_LOG:
                self.bdm_log.info("serverBDM set_initial_bdm Exception: {}".format([e]))
