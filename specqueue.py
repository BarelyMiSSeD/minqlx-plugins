# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# This is a queueing plugin for the minqlx admin bot.
# This plugin can be used alone or with the serverBDM.py plugin.
# Player placement into teams can be done using skill ratings (BDM 0r ELO) or used as a simple queue.
#
# This plugin is intended to help keep the game as enjoyable as possible,
#  without the hassles of people making teams uneven, or someone joining later than others,
#  but happening to hit the join button first and cutting in line when a play spot opens.
#
# The plugin will also attempt to keep team games even, when adding 2 players at once,
#  by putting players into the most appropriate team, based on team scores or player BDMs/ELOs.
#
# This plugin will spectate people when teams are uneven. It will, by default settings,
#  first look at player times then player scores to determine who, on the team with more players,
#  gets put to spectate. When a player gets put to spectate they will automatically get put into the
#  queue at the beginning of the line.
#
# There is also the option to have the players in spectate for too long (set with qlx_queueMaxSpecTime)
#  to be kicked. This will only kick the player, not do any kind of ban, so the player can reconnect immediately.
# This feature will not kick people with permission levels at or above the qlx_queueAdmin level,
#  or people who are in the queue.
#
# Use the command '!fix' to fix a player that is shown as sarge and not seen as an enemy or a teammate.
# This will set each player's model to the model recorded when they joined the server.
#
# See the following section for the meaning of the specqueue server cvars. The section can be copied as-is
# into a server config file and edited as desired.

# *** NOTE ****
# This plugin will unload any "set_configstring" hooks loaded by other scripts.
# The remove action is logged by printing the action to the console, check the minqlx.log.
# If this is not desired comment the self.remove_conflicting_hooks() line.
# Use minqlx.get_configstring(index) to be able to parse information from the config string.

"""
//set the minqlx permission level needed to admin this script
set qlx_queueAdmin "3"
//enable to use BDM/ELO in placement into teams when 2 players are put in together
//disable to use as generic queue system (0=off, 1=on)
set qlx_queueUseSkillPlacement "1"
//if pacing by skill rating (see qlx_queueUseSkillPlacement), use BDM or ELO (0=ELO, 1=BDM)
set qlx_queueUseRating "1"
//The script will try to place players in by BDM/ELO ranking, if this is set on (0=off 1=on) it will
// put the higher BDM/ELO player in the losing team if the score is greater than the qlx_queueTeamScoresDiff setting
set qlx_queuePlaceByTeamScores "1"
//Set the score difference used if qlx_queuePlaceByTeamScores is on
set qlx_queueTeamScoresDiff "3"
//Display the Queue message at the start of each round (0=off, 1=on, 2=display every 5th round)
set qlx_queueQueueMsg "1"
//Display the Spectate message at the start of each round
set qlx_queueSpecMsg "1"
//the minimum amount of players before the teams will be kept player number balanced
set qlx_queueMinPlayers "2"
//the maximum amount of players after which the teams will not be kept player number balanced
set qlx_queueMaxPlayers "30"
//use time played as a choosing factor to decide which player to spectate
set qlx_queueSpecByTime "1"
//use score played as a choosing factor to decide which player to spectate
set qlx_queueSpecByScore "1"
//set to either "score" or "time" to set which to use as the primary deciding factor in choosing a player to spectate
set qlx_queueSpecByPrimary "time"
//set to an amount of minutes a player is allowed to remain in spectate (while not in the queue) before the server will
// kick the player to make room for people who want to play. (valid values are greater than "0" and less than "9999")
set qlx_queueMaxSpecTime "9999"
// Set the maximum admin spectate time: 0=no Limit, Not 0=setting * qlx_queueMaxSpecTime
set qlx_queueAdminSpec "2"
// The amount of time in NO_COUNTDOWN_TEAM_GAMES it will give when teams are detected
//  as uneven before putting a player in spectate
set qlx_queueCheckTeamsDelay "5"
// Enable the fix the sarge player bug to execute at the start of a game
//  This will wait 2 seconds after the start of the game and set everyone's player model to the model being reported by
//   the server. It will not change what the player has set unless the server did not correctly receive the
//   player model information on player connect. This is an attempt to fix any occurrence of a player showing up as
//   the Sarge character of brown color, appearing like they are not on a team. (0=disable, 1=enable)
set qlx_queueResetPlayerModels "0"
// Enable to shuffle teams whenever the map changes, even if the same map is loaded again, or when a game is aborted
// (0=disable, 1=enable) (enabling not recommended if server is set to auto balance teams)
set qlx_queueShuffleOnMapChange "0"
// If shuffle on map change is enabled, sets the amount of time to wait before shuffling teams
// (must have qlx_queueShuffleOnMapChange enabled to work and a min of 10 and max of 30 seconds is required)
set qlx_queueShuffleTime "10"
// If shuffle on map change is enabled, displays a message to players counting down to the shuffle
// (0=disable, 1=center print every second, 2=center print every 5 seconds,
//    3=chat message every second, 4=chat message every 5 seconds)
set qlx_queueShuffleMessage "2"
// This will enable/disable the labeling of spectators with their spec/queue status (0=disable, 1=enable)
set qlx_queueShowQPosition "1"
// Chose the style of character surrounding the spec/queue label (default is brackets [] , ex. [1] )
// Start counting at 0 and chose the character position from the POSITION_LABEL list, so {} would
// be set qlx_queuePositionLabel "2". Set qlx_queuePositionLabel to one of these numbers or set it to a
// custom string, custom setting must have only two positions in, contained in quotes.
// 0="[]", 1="()", 2="{}", 3="<>", 4="--", 5="==", 6="||", 7="!!", 8="''", 9="..", 10="**", 11="〔〕", 12="《》"
// 13="〚〛", 14="  " (spaces)
set qlx_queuePositionLabel "0"  // custom ex: set qlx_queuePositionLabel "~~"
// This setting will perform check the clan tags saved in the database. Set it to the desired action.
// 0=Do Nothing, 1=Delete clan tags with special characters, 2=Delete all saved clan tags
set qlx_queueCleanClanTags "0"
// Will enforce even teams if enabled (0=disabled, 1=enabled)
set qlx_queueEnforceEvenTeams "1"
// Saves the retrieved player ELOs to the database. (0=disable, 1=enable)
// NOTE: Will overwrite any rankings set if blalance.py's !setelo is used. Makes balance.py get rankings faster.
set qlx_queueSaveEloToDatabase "1"
// Will request rankings from ELO_URL each map change. (0=disable, 1=enable)
set qlx_queueGetEloRatingsEachMap "1"
"""

import minqlx
import time
from threading import RLock
from random import randrange
import re
import requests

VERSION = "2.13.6"

# Add allowed spectator tags to this list. Tags can only be 5 characters long.
SPEC_TAGS = ("afk", "food", "away", "phone")

SUPPORTED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "ad", "1f", "har", "ffa", "race", "rr")
TEAM_BASED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "ad", "1f", "har")
NONTEAM_BASED_GAMETYPES = ("ffa", "race", "rr")
NO_COUNTDOWN_TEAM_GAMES = ("ft", "1f", "ad", "dom", "ctf")
RANKING_GAMETYPES = ("ft", "ca", "ctf", "ffa", "ictf", "tdm")
NON_ROUND_BASED_GAMETYPES = ("ffa", "race", "tdm", "ctf", "har", "dom", "rr")
BDM_KEY = "minqlx:players:{0}:bdm:{1}:{2}"
ELO_KEY = "minqlx:players:{0}:ratings:{1}"  # 0 == steam_id, 1 == short game type.
POSITION_LABELS = ("[]", "()", "{}", "<>", "--", "==", "||", "!!", "''", "..", "**", "〔〕", "《》", "〚〛", "  ")
ELO_URL = "qlstats.net"
DEFAULT_ELO = 1122

ENABLE_LOG = True  # set to True/False to enable/disable logging

if ENABLE_LOG:
    import traceback
    import logging
    import os
    from logging.handlers import RotatingFileHandler


# This is the class used to manage the player queue. I tried using the Queue that comes with python
# and tried just using a simple list, but both of those options had problems with the QL server's stability.
# I found that making my own queueing class eliminated the problems I was seeing as well as being able to make
# more efficient code to speed up execution time.
class PlayerQueue:
    def __init__(self):
        self._queue = []
        self._queue_player = []
        self._queue_times = {}
        self._q_count = 0
        self._lock = RLock()

    def __contains__(self, value):
        if self._q_count > 0:
            try:
                if isinstance(value, int):
                    return value in self._queue
                elif value.isdecimal():
                    return value in self._queue_times
                else:
                    return value in self._queue_player
            except:
                pass
        else:
            return False

    def __getitem__(self, value):
        if self._q_count > 0:
            try:
                if isinstance(value, int):
                    return self._queue[value]
                elif value.isdecimal():
                    if len(value) == 17:
                        return self._queue_times[value]
                    else:
                        return self._queue_player[int(value)]
            except:
                pass
        return None

    def __bool__(self):
        return self._q_count > 0

    def __len__(self):
        return self._q_count

    def size(self):
        return self._q_count

    @property
    def count(self):
        return self._q_count

    @property
    def next(self):
        return [self._queue[0], self._queue_player[0]]

    @next.setter
    def next(self, player):
        self.add_to_queue(player.steam_id, player, 0)

    def empty_queue(self):
        self.clear()

    def in_queue(self, sid=None, player=None):
        if not sid and not player:
            return False
        if player and not sid:
            sid = player.steam_id
        return self._q_count > 0 and sid in self._queue

    def add_to_queue(self, sid, player, pos=None):
        with self._lock:
            added = False
            if sid not in self._queue:
                if pos is None:
                    self._queue.append(sid)
                    self._queue_player.append(player)
                else:
                    self._queue.insert(pos, sid)
                    self._queue_player.insert(pos, player)
                self._q_count += 1
                self._queue_times[str(sid)] = time.time()
                added = True
            else:
                if pos is not None:
                    index = self.get_queue_position(sid)
                    if sid != index:
                        self._queue.remove(sid)
                        self._queue_player.remove(player)
                        self._queue.insert(pos, sid)
                        self._queue_player.insert(pos, player)
                        added = True
                    if str(sid) not in self._queue_times:
                        self._queue_times[str(sid)] = time.time()
            return added

    def get_next(self):
        return self.get_from_index()

    def get_from_queue(self, pos=None):
        if self._q_count > 0:
            pos = 0 if pos is None or pos <= 0 else pos - 1
            if pos >= self._q_count:
                pos = self._q_count - 1
            return self.get_from_index(pos)

    def get_from_index(self, pos=None):
        if self._q_count > 0:
            with self._lock:
                pos = 0 if pos is None or pos < 0 else pos
                if pos >= self._q_count:
                    pos = self._q_count - 1
                self._q_count -= 1
                sid = self._queue.pop(pos)
                player = self._queue_player.pop(pos)
                try:
                    ptime = self._queue_times.pop(str(sid))
                except IndexError:
                    ptime = 0
                return [sid, player, ptime]

    def get_two(self):
        if self._q_count > 1:
            with self._lock:
                self._q_count -= 2
                sid1 = self._queue.pop(0)
                player1 = self._queue_player.pop(0)
                p1time = None
                try:
                    p1time = self._queue_times.pop(str(sid1))
                except KeyError:
                    pass
                sid2 = self._queue.pop(0)
                player2 = self._queue_player.pop(0)
                p2time = None
                try:
                    p2time = self._queue_times.pop(str(sid2))
                except KeyError:
                    pass
                return [sid1, player1, sid2, player2, p1time, p2time]

    def remove_from_queue(self, sid, player):
        if self._q_count > 0:
            with self._lock:
                if sid in self._queue:
                    self._q_count -= 1
                    self._queue.remove(sid)
                    self._queue_player.remove(player)
                    try:
                        del self._queue_times[str(sid)]
                    except KeyError:
                        pass

    def get_queue_position(self, player):
        if player in self._queue:
            return self._queue.index(player)
        if player in self._queue_player:
            return self._queue_player.index(player)
        else:
            return -1

    def get_queue_time(self, sid):
        if str(sid) in self._queue_times:
            return self._queue_times[str(sid)]
        else:
            return None

    def add_to_times(self, sid):
        with self._lock:
            sid = str(sid)
            if sid not in self._queue_times:
                self._queue_times[sid] = time.time()
                self._q_count += 1

    def remove_from_times(self, sid):
        if self._q_count > 0:
            with self._lock:
                sid = str(sid)
                if sid in self._queue_times:
                    del self._queue_times[sid]
                    self._q_count -= 1

    def get_time(self, sid):
        sid = str(sid)
        if sid in self._queue_times:
            return self._queue_times[sid]
        else:
            return None

    def clear(self):
        self._queue = []
        self._queue_player = []
        self._queue_times = {}
        self._q_count = 0

    def queue(self):
        with self._lock:
            return [self._queue.copy(), self._queue_player.copy(), self._queue_times.copy()]

    def sids(self):
        with self._lock:
            return self._queue.copy()

    def players(self):
        with self._lock:
            return self._queue_player.copy()

    def times(self):
        with self._lock:
            return self._queue_times.copy()


class specqueue(minqlx.Plugin):
    def __init__(self):
        self._queue_label = "[]"
        if ENABLE_LOG:
            self.queue_log = logging.Logger(__name__)
            file_dir = os.path.join(minqlx.get_cvar("fs_homepath"), "logs")
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)

            file_path = os.path.join(file_dir, "specqueue.log")
            file_fmt = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
            file_handler = RotatingFileHandler(file_path, encoding="utf-8", maxBytes=3000000, backupCount=5)
            file_handler.setFormatter(file_fmt)
            self.queue_log.addHandler(file_handler)
            self.queue_log.info("============================= Logger started =============================")

        # queue cvars
        self.set_cvar_once("qlx_queueAdmin", "3")
        self.set_cvar_once("qlx_queueUseSkillPlacement", "1")
        self.set_cvar_once("qlx_queueUseRating", "1")
        self.set_cvar_once("qlx_queuePlaceByTeamScores", "1")
        self.set_cvar_once("qlx_queueTeamScoresDiff", "3")
        self.set_cvar_once("qlx_queueQueueMsg", "1")
        self.set_cvar_once("qlx_queueSpecMsg", "1")
        self.set_cvar_once("qlx_queueMinPlayers", "2")
        self.set_cvar_once("qlx_queueMaxPlayers", "30")
        self.set_cvar_once("qlx_queueSpecByTime", "1")
        self.set_cvar_once("qlx_queueSpecByScore", "1")
        self.set_cvar_once("qlx_queueSpecByPrimary", "time")
        self.set_cvar_once("qlx_queueMaxSpecTime", "9999")  # time in minutes
        self.set_cvar_once("qlx_queueAdminSpec", "2")  # 0=no Limit, !0=setting * qlx_queueMaxSpecTime
        self.set_cvar_once("qlx_queueCheckTeamsDelay", "5")
        self.set_cvar_once("qlx_queueResetPlayerModels", "0")
        self.set_cvar_once("qlx_queueShuffleOnMapChange", "0")
        self.set_cvar_once("qlx_queueShuffleTime", "10")
        self.set_cvar_once("qlx_queueShuffleMessage", "2")
        self.set_cvar_once("qlx_queueShowQPosition", "1")
        self.set_cvar_once("qlx_queuePositionLabel", "0")
        self.set_cvar_once("qlx_queueCleanClanTags", "0")
        self.set_cvar_once("qlx_queueEnforceEvenTeams", "1")
        self.set_cvar_once("qlx_queueSaveEloToDatabase", "1")
        self.set_cvar_once("qlx_queueGetEloRatingsEachMap", "1")

        # Minqlx bot Hooks
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("game_start", self.handle_game_start)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("round_countdown", self.handle_round_countdown)
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("round_end", self.handle_round_end)
        self.add_hook("death", self.death_monitor)
        self.add_hook("player_connect", self.handle_player_connect)
        self.add_hook("player_loaded", self.handle_player_loaded, priority=minqlx.PRI_LOWEST)
        self.add_hook("player_disconnect", self.handle_player_disconnect, priority=minqlx.PRI_HIGH)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("team_switch_attempt", self.handle_team_switch_attempt, priority=minqlx.PRI_HIGH)
        self.add_hook("set_configstring", self.handle_set_config_string, priority=minqlx.PRI_HIGHEST)
        self.add_hook("client_command", self.handle_client_command)
        self.add_hook("vote_ended", self.handle_vote_ended)
        self.add_hook("console_print", self.handle_console_print)
        self.add_hook("map", self.handle_map)

        # Minqlx bot commands
        self.add_command(("q", "queue"), self.cmd_list_queue)
        self.add_command(("s", "specs"), self.cmd_list_specs)
        self.add_command([x for x in SPEC_TAGS], self.cmd_go_afk)
        self.add_command(("back", "here"), self.cmd_here)
        self.add_command("tags", self.cmd_tags)
        self.add_command(("addqueue", "addq"), self.cmd_queue_add)
        self.add_command(("qversion", "qv"), self.cmd_qversion)
        self.add_command("ignore", self.ignore_imbalance, self.get_cvar("qlx_queueAdmin", int))
        self.add_command("latch", self.ignore_imbalance_latch, self.get_cvar("qlx_queueAdmin", int))
        self.add_command("fix", self.reset_model, self.get_cvar("qlx_queueAdmin", int))
        self.add_command(("resetqueue", "rq", "fq"), self.reset_queue, self.get_cvar("qlx_queueAdmin", int))
        self.add_command(("queuestatus", "qs"), self.get_current_settings, 5)
        self.add_command("getspec", self.get_spec, 5)

        # Script Variables, Lists, and Dictionaries
        self._queue = PlayerQueue()
        self._spec = PlayerQueue()
        self._join = PlayerQueue()
        self._afk = PlayerQueue()
        self._players = []
        self.red_locked = False
        self.blue_locked = False
        self.free_locked = False
        self.end_screen = False
        self.displaying_queue = False
        self.displaying_spec = False
        self.in_countdown = False
        self.death_count = 0
        self.q_game_info = [self.game.type_short, self.get_cvar("teamsize", int), self.get_cvar("fraglimit", int)]
        self._round = 0
        self.uneven_teams_move_to_spec = {}
        self._ignore = False
        self._latch_ignore = False
        self._ignore_msg_already_said = False
        self._player_models = {}
        self._checking_opening = None
        self._countdown = False
        self._queue_tags = False
        self._specPlayer = []
        self._afk_tag = {}
        self.retrieving_elo = False
        self.elo_ratings = {}
        self.elo_lock = RLock()

        # Initialize Commands
        self.add_spectators()
        self.add_join_times()
        self.record_player_models()
        self.update_queue_tags()
        self.check_clan_tags()
        self.remove_conflicting_hooks()
        self.set_queue_label()
        self.get_cvars()

    # ==============================================
    #               Event Handler's
    # ==============================================
    def handle_player_connect(self, player):
        self.process_player_connect(player)
        return

    def process_player_connect(self, player):
        try:
            if ENABLE_LOG:
                self.queue_log.info("specqueue process player connect: {}".format(player))
            if not self._queue.in_queue(player=player):
                self.add_to_spec(player)
                self.remove_from_queue(player)
                self.remove_from_join(player)
            self.request_elo_rating(player.steam_id)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_player_connect Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def handle_player_loaded(self, player):
        self.process_player_loaded(player)
        return

    def process_player_loaded(self, player):
        try:
            if ENABLE_LOG:
                self.queue_log.info("specqueue process player loaded: {}".format(player))
            self._player_models[player.id] = player.model
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_player_loaded Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def handle_player_disconnect(self, player, reason):
        self.process_payer_disconnect(player)
        return

    def process_payer_disconnect(self, player):
        try:
            with self.elo_lock:
                try:
                    del self.elo_ratings[str(player.steam_id)]
                except KeyError:
                    pass
            if ENABLE_LOG:
                self.queue_log.info("specqueue process player disconnect: {}".format(player))
            try:
                self.remove_from_spec(player)
            except Exception as e:
                if ENABLE_LOG:
                    self.queue_log.info("specqueue remove from spec on disconnect: {} Exception: {}".format(player, e))
            try:
                self.remove_from_queue(player)
            except Exception as e:
                if ENABLE_LOG:
                    self.queue_log.info("specqueue remove from queue on disconnect: {} Exception: {}".format(player, e))
            try:
                self.remove_from_join(player)
            except Exception as e:
                if ENABLE_LOG:
                    self.queue_log.info("specqueue remove from join on disconnect: {} Exception: {}".format(player, e))
            try:
                self.remove_from_afk(player, False)
            except Exception as e:
                if ENABLE_LOG:
                    self.queue_log.info("specqueue remove from afk on disconnect: {} Exception: {}".format(player, e))

            self.check_for_opening(0.5)
            if self.q_game_info[0] in NO_COUNTDOWN_TEAM_GAMES and not self.end_screen and\
                    not (self.red_locked or self.blue_locked or self.free_locked):
                self.look_at_teams(1.0)
            if player.id in self._player_models:
                del self._player_models[player.id]
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_player_disconnect Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))
        self.update_queue_tags()

    def handle_team_switch(self, player, old_team, new_team):
        self.process_team_switch(player, new_team)
        return

    def process_team_switch(self, player, new_team):
        if ENABLE_LOG:
            self.queue_log.info("specqueue process team switch: {} to {}".format(player, new_team))
        if new_team != "spectator":
            try:
                self.remove_from_spec(player)
                self.remove_from_queue(player)
                if str(player.steam_id) not in self._join:
                    self.add_to_join(player)
                player.clan = player.clan
            except Exception as e:
                if ENABLE_LOG:
                    self.queue_log.info("specqueue handle_team_switch not to spectator Exception: {}\n{}"
                                        .format(type(e).__name__, traceback.format_exc()))
        else:
            try:
                if not self.end_screen:
                    self.check_for_opening(0.2)
                    if self.q_game_info[0] in NO_COUNTDOWN_TEAM_GAMES and\
                            not (self.red_locked or self.blue_locked or self.free_locked):
                        self.look_at_teams(1.0)

                @minqlx.delay(1)
                def check_spectator():
                    if not self._queue.in_queue(player=player):
                        self.add_to_spec(player)
                    self.remove_from_join(player)

                if player.steam_id in self.uneven_teams_move_to_spec:
                    del self.uneven_teams_move_to_spec[player.steam_id]
                else:
                    check_spectator()
            except Exception as e:
                if ENABLE_LOG:
                    self.queue_log.info("specqueue handle_team_switch to spectator Exception: {}\n{}"
                                        .format(type(e).__name__, traceback.format_exc()))
        self.update_queue_tags()

    def handle_team_switch_attempt(self, player, old_team, new_team):
        if ENABLE_LOG:
            self.queue_log.info("specqueue handle team switch attempt: {} old_team={} new_team={}"
                                .format(player, old_team, new_team))
        if self.q_game_info[0] in SUPPORTED_GAMETYPES and new_team != "spectator" and old_team == "spectator":
            teams = self.teams()
            at_max_players = False
            join_locked = False
            self.remove_from_afk(player)
            if self.q_game_info[0] in TEAM_BASED_GAMETYPES:
                if len(teams["red"]) + len(teams["blue"]) >= self.get_max_players():
                    at_max_players = True
                join_locked = self.free_locked
            elif self.q_game_info[0] in NONTEAM_BASED_GAMETYPES:
                if len(self.teams()["free"]) >= self.get_max_players():
                    at_max_players = True
                join_locked = self.red_locked or self.blue_locked
            if self._queue or join_locked or self.game and self.game.state in ["in_progress", "countdown"] or\
                    at_max_players:
                self.add_to_queue(player)
                self.remove_from_spec(player)
                self.check_for_opening(0.2)
                self.update_queue_tags()
                return minqlx.RET_STOP_ALL

    def handle_set_config_string(self, index, values):
        if not values:
            return
        if 529 <= index <= 592:
            if not self.get_cvar("qlx_queueShowQPosition", bool):
                return
            args = minqlx.parse_variables(values, ordered=True)
            # If the config_string is not complete, don't allow it to be set on the server
            if 'n' not in args:
                return minqlx.RET_STOP_ALL
            # This check is due to bots being added to the game, which don't have config_string steam ids
            if 'st' in args:
                s_id = args['st']
                sid = int(s_id)
            else:
                sid = self.player(index - 529).steam_id
                s_id = str(sid)
            # If the player is in spectate and queue tags are on, process the spectator tag
            if args['t'] == '3' and self._queue_tags:
                if not self._queue_label:
                    self._queue_label = "[]"
                # if the player is in the queue, set the queue position tag
                if sid in self._queue:
                    args['xcn'] = args['cn'] = "{}{}{}" \
                        .format(self._queue_label[0], self._queue.get_queue_position(sid) + 1, self._queue_label[1])
                # otherwise set the spectator tag
                else:
                    clan = None
                    location = "minqlx:players:{}:clantag".format(s_id)
                    if location in self.db:
                        clan = self.db[location]
                    if s_id in self._afk and clan not in SPEC_TAGS:
                        args['xcn'] = args['cn'] = "{}{}{}"\
                            .format(self._queue_label[0], self._afk_tag[s_id], self._queue_label[1])
                    elif clan in SPEC_TAGS:
                        if 3 < len(clan):
                            args['xcn'] = args['cn'] = "{}".format(clan)
                        else:
                            args['xcn'] = args['cn'] = "{}{}{}".format(self._queue_label[0], clan, self._queue_label[1])
                    else:
                        args['xcn'] = args['cn'] = "{}s{}".format(self._queue_label[0], self._queue_label[1])
            # Otherwise set the clan tag, if a clan tag is saved
            else:
                location = "minqlx:players:{}:clantag".format(s_id)
                if location in self.db:
                    args['xcn'] = args['cn'] = self.db[location]
                else:
                    args.pop('xcn', None)
                    args.pop('cn', None)
            return ''.join(["\\{}\\{}".format(key, value) for key, value in args.items()]).lstrip("\\")
        # process the server teamsize and fraglimit settings
        elif index == 0:
            args = minqlx.parse_variables(values)
            self.q_game_info[2] = int(args['fraglimit'])
            teamsize = int(args['teamsize'])
            if self.q_game_info[1] != teamsize:
                self.q_game_info[1] = teamsize
                if not self.end_screen:
                    self.check_for_opening(1.5)

    def update_queue_tags(self):
        if self.get_cvar("qlx_queueShowQPosition", bool):
            self._queue_tags = True
            for player in self.teams()["spectator"]:
                player.clan = player.clan
        else:
            self._queue_tags = False

    def handle_client_command(self, player, command):
        self.process_client_command(player, command)
        return

    def process_client_command(self, player, command):
        try:
            @minqlx.delay(0.2)
            def spec_player():
                if command == "team s" and player in self.teams()["spectator"]:
                    self.add_to_spec(player)
                    self.remove_from_queue(player)
                    self.remove_from_join(player)
                    player.center_print("^6You are set to spectate only")
            spec_player()
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_client_command Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))
        self.update_queue_tags()

    def handle_new_game(self):
        self.process_new_game()
        return

    def process_new_game(self):
        try:
            if ENABLE_LOG:
                self.queue_log.info("specqueue process new game")
            self.q_game_info = [self.game.type_short, self.get_cvar("teamsize", int), self.get_cvar("fraglimit", int)]
            self.end_screen = False
            self.displaying_queue = False
            self.displaying_spec = False

            if self.q_game_info[0] not in SUPPORTED_GAMETYPES:
                self._queue.clear()
                self.msg("^1This gametype is not supported by the queueing system. Queue functions are not available.")
            else:
                self.check_for_opening(0.5)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_new_game Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def handle_game_start(self, data):
        self.process_game_start()
        return

    def process_game_start(self):
        try:
            self.check_spec_time()

            @minqlx.thread
            def t():
                if self.q_game_info[0] == "ft":
                    countdown = self._specPlayer[5]
                else:
                    countdown = self._specPlayer[6]
                time.sleep(max(countdown / 1000 - 0.8, 0))
                if not (self.red_locked or self.blue_locked or self.free_locked):
                    self.even_the_teams()

            if ENABLE_LOG:
                self.queue_log.info("specqueue process game start")

            t()

            if self.get_cvar("qlx_queueResetPlayerModels", bool):
                self.reset_players_model(5)

        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_game_start Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def handle_map(self, mapname, factory):
        self.process_map()
        self.get_cvars()
        return

    @minqlx.delay(0.3)
    def process_map(self):
        try:
            if ENABLE_LOG:
                self.queue_log.info("specqueue process map")
            self.q_game_info = [self.game.type_short, self.get_cvar("teamsize", int), self.get_cvar("fraglimit", int)]
            self._ignore = False
            self._ignore_msg_already_said = False
            self.end_screen = False
            self.check_spec_time()
            self.death_count = 0
            self.auto_shuffle_player_teams()
            if self.get_cvar("qlx_queueGetEloRatingsEachMap", bool):
                players_sid = [p.steam_id for p in self.players()]
                self.request_elo_rating(players_sid)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_map Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def handle_game_end(self, data):
        if ENABLE_LOG:
            self.queue_log.info("specqueue handle game end: {}".format(data))
        if not data["ABORTED"]:
            self.end_screen = True
        return

    def handle_round_countdown(self, round_num):
        self.process_round_countdown(round_num)
        return

    def process_round_countdown(self, round_num):
        try:
            self._countdown = True
            self._round = round_num
            self._ignore = False
            self._ignore_msg_already_said = False
            self.check_for_opening(0.2)
            if self.get_cvar("qlx_queueQueueMsg", bool):
                self.cmd_list_queue()
            if self.get_cvar("qlx_queueSpecMsg", bool):
                self.cmd_list_specs()
            self.check_queue(0.2)
            self.check_spec(0.2)
            if self.q_game_info[0] and not (self.red_locked or self.blue_locked or self.free_locked):
                self.look_at_teams()
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_round_countdown Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def handle_round_start(self, number):
        self.process_round_start()
        return

    def process_round_start(self):
        try:
            if not self._countdown and not (self.red_locked or self.blue_locked or self.free_locked):
                self.even_the_teams()
                self.check_queue(2)
                self.check_spec(2)
            self._countdown = False
            self.check_for_opening(0.2)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_round_start Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def handle_round_end(self, data):
        self.process_round_end()
        return

    def process_round_end(self):
        try:
            if self.q_game_info[0] in NO_COUNTDOWN_TEAM_GAMES:
                self.check_for_opening(0.2)
                if not (self.red_locked or self.blue_locked or self.free_locked):
                    self.even_the_teams(True)
                if self.get_cvar("qlx_queueQueueMsg", bool):
                    self.cmd_list_queue()
                if self.get_cvar("qlx_queueSpecMsg", bool):
                    self.cmd_list_specs()
            self.check_spec_time()
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_round_end Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def death_monitor(self, victim, killer, data):
        self.process_death_monitor()
        return

    def process_death_monitor(self):
        try:
            if self.game and self.game.state in ["in_progress", "countdown"]:
                if self.q_game_info[0] in NON_ROUND_BASED_GAMETYPES:
                    self.death_count += 1
                    if self.death_count > 5 and self.death_count > self.q_game_info[2] / 5:
                        self.check_for_opening(0.2)
                        if self.get_cvar("qlx_queueQueueMsg", bool):
                            self.cmd_list_queue()
                        if self.get_cvar("qlx_queueSpecMsg", bool):
                            self.cmd_list_specs()
                        self.check_queue(0.2)
                        self.check_spec(0.2)
                        self.death_count = 0
                        self.check_spec_time()
                if self.q_game_info[0] in TEAM_BASED_GAMETYPES:
                    self.check_for_opening(0.2)
        except Exception as e:
            if "NoneType" not in e:
                if ENABLE_LOG:
                    self.queue_log.info("specqueue death_monitor Exception: {}\n{}"
                                        .format(type(e).__name__, traceback.format_exc()))

    def handle_console_print(self, text):
        self.process_console_print(text)
        return

    def process_console_print(self, text):
        try:
            if "locked" in text:
                if text.find("The RED team is now locked") != -1:
                    self.red_locked = True
                elif text.find("The BLUE team is now locked") != -1:
                    self.blue_locked = True
                if text.find("The FREE team is now locked") != -1:
                    self.free_locked = True
                elif text.find("The RED team is now unlocked") != -1:
                    self.red_locked = False
                elif text.find("The BLUE team is now unlocked") != -1:
                    self.blue_locked = False
                elif text.find("The FREE team is now unlocked") != -1:
                    self.free_locked = False
                self.check_for_opening(0.2)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_console_print Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))


    def handle_vote_ended(self, votes, vote, args, passed):
        self.process_vote_ended(vote, passed)
        return

    def process_vote_ended(self, vote, passed):
        try:
            if passed and vote == "teamsize":
                self.check_for_opening(2.5)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue handle_vote_ended Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    # ==============================================
    #               Plugin functions
    # ==============================================
    # set the label used for spectators, if enabled
    def set_queue_label(self):
        label = self.get_cvar("qlx_queuePositionLabel", str)
        try:
            self._queue_label = POSITION_LABELS[int(label)]
        except ValueError:
            self._queue_label = label
        except IndexError:
            self._queue_label = POSITION_LABELS[0]

    # removes any set_configstring hooks used by other plugins
    @minqlx.delay(2)
    def remove_conflicting_hooks(self):
        if self.get_cvar("qlx_queueShowQPosition", bool):
            hook_events = ["set_configstring"]
            remove_from = ["clan"]
            loaded_scripts = self.plugins
            loaded_scripts.pop(self.__class__.__name__)
            for script, handler in loaded_scripts.items():
                try:
                    if script in remove_from:
                        for hook in handler.hooks:
                            for event in hook_events:
                                if event == hook[0]:
                                    if ENABLE_LOG:
                                        self.queue_log.info("specqueue: Removing event hook ^7{}"
                                                            " ^1used in ^7{} ^1plugin"
                                                            .format(event, script))
                                    handler.remove_hook(event, hook[1], hook[2])
                except:
                    continue

    # Deletes saved clan tags that are not simple in formation
    def check_clan_tags(self):
        level = self.get_cvar("qlx_queueCleanClanTags", int)
        if level:
            keys = self.db.keys("minqlx:players:*:clantag")
            for tag in keys:
                clan_tag = self.db.get(tag)
                if level == 1:
                    check_tag = [ord(c) for c in clan_tag]
                    for char in check_tag:
                        if 0x20 > char or 0x7F < char:
                            del self.db[tag]
                            break
                    length = len(re.sub(r"\^[0-9]", "", clan_tag))
                    if length == 0 or length > 5:
                        del self.db[tag]
                else:
                    del self.db[tag]

    # Execute a shuffle command if the game is a team based game type
    @minqlx.thread
    def auto_shuffle_player_teams(self):
        try:
            if self.get_cvar("qlx_queueShuffleOnMapChange", bool) and self.q_game_info[0] in TEAM_BASED_GAMETYPES and\
                    len(self.players()) > 2 and self.game.state == "warmup":
                count = 0
                saved_time = self.get_cvar("qlx_queueShuffleTime", int)
                shuffle_time = saved_time if 10 <= saved_time <= 30 else 10
                message_setting = self.get_cvar("qlx_queueShuffleMessage", int)
                if message_setting:
                    while count < shuffle_time:
                        execute_time = shuffle_time - count
                        if message_setting == 2:
                            if not count % 5:
                                self.center_print("^7Shuffling teams in {} second{}"
                                                  .format(execute_time, "s" if execute_time > 1 else ""))
                        elif message_setting == 3:
                            self.msg("^6Shuffling teams in {} second{}"
                                     .format(execute_time, "s" if execute_time > 1 else ""))
                        elif message_setting == 4:
                            if not count % 5:
                                self.msg("^6Shuffling teams in {} second{}"
                                         .format(execute_time, "s" if execute_time > 1 else ""))
                        else:
                            self.center_print("^7Shuffling teams in {} second{}"
                                              .format(execute_time, "s" if execute_time > 1 else ""))
                        count += 1
                        time.sleep(1)
                    if message_setting < 3:
                        self.center_print("^7Shuffling teams")
                    else:
                        self.msg("^6Shuffling teams")
                else:
                    time.sleep(shuffle_time)
                if ENABLE_LOG:
                    self.queue_log.info("specqueue auto_shuffle_player_teams Teams")
                self.shuffle_players()
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue auto_shuffle_player_teams Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    @minqlx.next_frame
    def shuffle_players(self):
        if ENABLE_LOG:
            self.queue_log.info("specqueue Shuffling Teams")
        minqlx.console_command("forceshuffle")

    def get_max_players(self):
        try:
            max_players = self.get_cvar("teamsize", int)
            if self.q_game_info[0] in TEAM_BASED_GAMETYPES:
                max_players *= 2
            if max_players == 0:
                max_players = self.get_cvar("sv_maxClients", int)
            return max_players
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue get max players Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def add_to_queue_pos(self, player, pos):
        try:
            self.remove_from_spec(player)
            if str(player.steam_id) not in self._join:
                self.add_to_join(player)
            self._queue.add_to_queue(player.steam_id, player, pos)
            self.cmd_list_queue()
            self.check_for_opening(0.5)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue add to queue pos Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def add_to_queue(self, player):
        try:
            self.remove_from_spec(player)
            if str(player.steam_id) not in self._join:
                self.add_to_join(player)
            self._queue.add_to_queue(player.steam_id, player)
            position = self._queue.get_queue_position(player)
            player.center_print("^7You are in the ^4Queue^7 position ^1{}^7\nType ^4{}q ^7to show the queue"
                                .format(position + 1, self.get_cvar("qlx_commandPrefix")))
            self.check_for_opening(0.2)
            if ENABLE_LOG:
                self.queue_log.info("specqueue add to queue: {}".format(player))
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue add to queue Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def remove_from_queue(self, player):
        try:
            if player and self._queue.in_queue(player=player):
                self._queue.remove_from_queue(player.steam_id, player)
        except Exception as e:
            if ENABLE_LOG:
                raise KeyError("remove from queue Exception: {}\n{}"
                               .format(type(e).__name__, traceback.format_exc()))

    def check_queue(self, delay=0.1):
        try:
            if not self.end_screen and not self.displaying_queue and self._queue\
                    and self.get_cvar("qlx_queueQueueMsg", bool):
                self.displaying_queue = True
                self.queue_message(delay)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue check queue Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    @minqlx.thread
    def queue_message(self, delay):
        try:
            n = self._queue.players()
            time.sleep(delay)
            queue_show = self.get_cvar("qlx_queueQueueMsg", int)
            if queue_show == 2 and self._round % 5 != 0:
                self.displaying_queue = False
                return
            count = 1
            for p in n:
                try:
                    p.center_print("^7You are in ^4Queue ^7position ^1{}".format(count))
                except Exception as e:
                    if ENABLE_LOG:
                        self.queue_log.info("specqueue Queue Message Exception: {}\n{}"
                                            .format(type(e).__name__, traceback.format_exc()))
                finally:
                    count += 1
            self.displaying_queue = False
        except Exception as e:
            self.queue_log.info("specqueue queue message Exception: {}\n{}"
                                .format(type(e).__name__, traceback.format_exc()))

    def add_spectators(self):
        try:
            for player in self.teams()["spectator"]:
                self.add_to_spec(player)
        except Exception as e:
            raise KeyError("add spectators Exception: { ; {}"
                           .format(type(e).__name__, traceback.format_exc()))

    def add_to_spec(self, player):
        try:
            self._spec.add_to_times(player.steam_id)
            player.center_print("^6Spectate Mode\n^7Type ^4!s ^7to show spectators.")
        except Exception as e:
            raise KeyError("add to spec Exception: {} ; {}"
                           .format(type(e).__name__, traceback.format_exc()))

    def remove_from_spec(self, player):
        try:
            if player:
                self._spec.remove_from_times(player.steam_id)
        except Exception as e:
            raise KeyError("remove from spec Exception: {} ; {}"
                           .format(type(e).__name__, traceback.format_exc()))

    def check_spec(self, delay=0.0):
        try:
            if not self.end_screen and not self.displaying_spec and self._spec.count > 0\
                    and self.get_cvar("qlx_queueSpecMsg", bool):
                self.displaying_spec = True
                self.spec_message(delay)
        except Exception as e:
            raise KeyError("check spec Exception: {} ; {}"
                           .format(type(e).__name__, traceback.format_exc()))

    @minqlx.thread
    def spec_message(self, delay=0.0):
        try:
            time.sleep(delay)
            spec_show = self.get_cvar("qlx_queueSpecMsg", int)
            spectators = self.teams()["spectator"]
            if self._spec.count > 0 and len(spectators) > 0:
                s = self._spec.times()
                for p, t in s.items():
                    spec = self.player(int(p))
                    if spec in spectators:
                        if spec_show == 2 and self._round % 5 != 0:
                            continue
                        time_in_spec = round((time.time() - t))
                        if time_in_spec / 60 > 1:
                            spec_time = "^7{}^4m^7:{}^4s^7".format(int(time_in_spec / 60), time_in_spec % 60)
                        else:
                            spec_time = "^7{}^4s^7".format(time_in_spec)
                        max_spec_time = self.get_cvar("qlx_queueMaxSpecTime", int)
                        admin = self.get_cvar("qlx_queueAdmin", int)
                        admin_multiplier = self.get_cvar("qlx_queueAdminSpec", int)
                        permission = self.db.get_permission(int(p))
                        if 0 < max_spec_time < 9998 and permission < admin:
                            spec.center_print("^6Spectate Mode for {}\n^7Join the game to ^1play ^7or enter the"
                                              " ^4Queue.\nYou can remain in spectate for ^1{} ^7minutes."
                                              .format(spec_time, max_spec_time))
                        elif permission >= admin and admin_multiplier:
                            spec.center_print("^6Spectate Mode for {}\n^7Join the game to ^1play ^7or enter the"
                                              " ^4Queue.\nYou can remain in spectate for ^1{} ^7minutes."
                                              .format(spec_time, max_spec_time * admin_multiplier))
                        else:
                            spec.center_print("^6Spectate Mode for {}\n^7Join the game to ^1play ^7or enter the ^4Queue"
                                              .format(spec_time))
            self.displaying_spec = False
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue spec message Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def check_queue_status(self):
        if self._checking_opening and time.time() - self._checking_opening > 1:
            self._checking_opening = None
            self.check_for_opening(0.1)

    @minqlx.thread
    def check_for_opening(self, delay=0.0):
        if self.end_screen:
            return
        if self._checking_opening or not self._queue:
            self.check_queue_status()
            return
        self._checking_opening = time.time()
        if delay > 0.0:
            time.sleep(delay)
        finished = False
        try:
            teams = self.teams()
            state = self.game.state
            max_players = self.get_max_players()
            red_players = len(teams["red"])
            blue_players = len(teams["blue"])
            free_players = len(teams["free"])
            if self.q_game_info[0] in NONTEAM_BASED_GAMETYPES:
                if free_players < max_players and not self.free_locked:
                    finished = self.place_in_team(max_players - free_players, "free")
                elif state == "warmup" and free_players > max_players:
                    fixed = self.fix_free(free_players, max_players, teams)
                    if not fixed:
                        if ENABLE_LOG:
                            self.queue_log.info("specqueue check_for_opening Fix Free error.")

            elif self.q_game_info[0] in TEAM_BASED_GAMETYPES:
                team_size = int(max_players / 2)
                if not self.red_locked and not self.blue_locked and (red_players + blue_players) < max_players:
                    fix_teams = state == "warmup" and red_players > team_size or blue_players > team_size
                    if fix_teams:
                        fixed = self.fix_teams(red_players, blue_players, max_players, teams)
                        if not fixed:
                            if ENABLE_LOG:
                                self.queue_log.info("specqueue check_for_opening Fix Teams error.")
                    difference = red_players - blue_players
                    if difference < 0:
                        finished = self.place_in_team(abs(difference), "red")
                    elif difference > 0:
                        finished = self.place_in_team(difference, "blue")
                    else:
                        if self._queue.count > 1:
                            if red_players < team_size and blue_players < team_size:
                                finished = self.place_in_both()
                        elif state == "warmup":
                            if blue_players < team_size:
                                finished = self.place_in_team(1, "blue")
                            elif red_players < team_size:
                                finished = self.place_in_team(1, "red")
                elif state == "warmup" and (red_players + blue_players) >= max_players or\
                        red_players > team_size or blue_players > team_size:
                    self.fix_teams(red_players, blue_players, max_players, teams)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue check_for_opening Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))
        self._checking_opening = None
        return finished

    def place_in_team(self, amount, team):
        try:
            if not self.end_screen:
                count = 0
                teams = self.teams()
                while count < amount and self._queue:
                    p = self._queue.get_next()
                    if p[1] in teams["spectator"]and p[1].connection_state == "active":
                        self.team_placement(p[1], team)
                        if team == "red":
                            placement = "^1red ^7team"
                        elif team == "blue":
                            placement = "^4blue ^7team"
                        else:
                            placement = "^2battle"
                        self.msg("{} ^7has joined the {}.".format(p[1], placement))
                        count += 1
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue Place in Team Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))
            for player in self.teams()["spectator"]:
                player.tell("^1Error in player placement in team. ^6Check your position in the queue.")
        return True

    def place_in_both(self):
        try:
            if not self.end_screen and self._queue.count > 1:
                teams = self.teams()
                spectators = teams["spectator"]
                players = self._queue.get_two()
                p1 = None
                p2 = None
                if players[1].connection_state != "active" or players[1] not in spectators:
                    p1 = self._queue.get_next()
                if players[3].connection_state != "active" or players[3] not in spectators:
                    p2 = self._queue.get_next()
                if p1 and p2:
                    players = [p1[0], p1[1], p2[0], p2[1], p1[2], p2[2]]
                elif p1:
                    players = [p1[0], p1[1], players[2], players[3], p1[2], players[5]]
                elif p2:
                    players = [players[0], players[1], p2[0], p2[1], players[4], p2[2]]
                # Get red team's and blue team's score so the correct player placements can be executed
                red_score = int(self.game.red_score)
                blue_score = int(self.game.blue_score)
                score_diff = abs(red_score - blue_score) >= self.get_cvar("qlx_queueTeamScoresDiff", int)
                if self.q_game_info[0] in RANKING_GAMETYPES and self.get_cvar("qlx_queueUseSkillPlacement", bool):
                    red_rating, blue_rating, p1_rating, p2_rating = self.get_ratings(players[0], players[2], teams)
                    self.msg('^2Placing players by ^3{} ^2Balance Used ^7Red: ^1{} ^7Blue: ^4{} '
                             .format('BDM' if self.get_cvar("qlx_queueUseRating", bool) else 'ELO',
                                     red_rating, blue_rating))
                    # set team related variables initial values
                    # If the team's score difference is over "qlx_queuesTeamScoresAmount" and
                    #  "qlx_queuesPlaceByTeamScore" is enabled players will be placed with the higher BDM/ELO
                    #  player going to the lower scoring team regardless of average team BDMs/ELOs
                    place_by_team_scores = False
                    if self.get_cvar("qlx_queuePlaceByTeamScores", bool) and score_diff:
                        place_by_team_scores = True
                        if p1_rating > p2_rating:
                            placement = ["blue", "red"] if red_score > blue_score else ["red", "blue"]
                        else:
                            placement = ["red", "blue"] if red_score > blue_score else ["blue", "red"]
                    # Executes if the 'place by team score' doesn't execute and sets player
                    #   with higher BDM/ELO on the team with the lower average BDM/ELO.
                    else:
                        if red_rating > blue_rating:
                            placement = ["blue", "red"] if p1_rating > p2_rating else ["red", "blue"]
                        elif blue_rating > red_rating:
                            placement = ["red", "blue"] if p1_rating > p2_rating else ["blue", "red"]
                        else:
                            if red_score > blue_score:
                                placement = ["blue", "red"] if p1_rating > p2_rating else ["red", "blue"]
                            else:
                                placement = ["red", "blue"] if p1_rating > p2_rating else ["blue", "red"]
                    if place_by_team_scores:
                        self.msg("^3Due to team score difference, placing players based on team score, not {} balance."
                                 .format('BDM' if self.get_cvar("qlx_queueUseRating", bool) else 'ELO'))
                    self.team_placement(players[1], placement[0])
                    self.msg("{0} ^7:{1}{3} ^7has joined the {1}{2} ^7team."
                             .format(players[1], "^1" if placement[0] == "red" else "^4", placement[0], p1_rating))
                    self.team_placement(players[3], placement[1])
                    self.msg("{0} ^7:{1}{3} ^7has joined the {1}{2} ^7team."
                             .format(players[3], "^1" if placement[1] == "red" else "^4", placement[1], p2_rating))
                else:
                    self.team_placement(players[1], "blue")
                    self.msg("{} ^7has joined the ^4blue ^7team.".format(players[1]))
                    self.team_placement(players[3], "red")
                    self.msg("{} ^7has joined the ^1red ^7team.".format(players[3]))
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue Place in Both Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))
            for player in self.teams()["spectator"]:
                player.tell("^1Error in player(s) placement in team. ^6Check your position in the queue.")
        return True

    def fix_teams(self, red, blue, max_players, player_teams):
        try:
            teams = player_teams.copy()
            total = red + blue
            team_size = int(max_players / 2)
            while total > max_players:
                if red > team_size:
                    self.get_player_for_spec(teams["red"])
                    self.team_placement(self._players[0], "spectator", True)
                    red -= 1
                    total -= 1
                if blue > team_size:
                    self.get_player_for_spec(teams["blue"])
                    self.team_placement(self._players[0], "spectator", True)
                    blue -= 1
                    total -= 1
            difference = red - blue
            while difference > 0:
                self.team_placement(teams["red"][0], "blue")
                teams["blue"].append(teams["red"].pop(0))
                difference -= 1
            while difference < 0:
                self.team_placement(teams["blue"][0], "red")
                teams["red"].append(teams["blue"].pop(0))
                difference += 1
            return True
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue fix_teams Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def fix_free(self, free, max_players, player_teams):
        try:
            teams = player_teams.copy()
            while free > max_players:
                self.get_player_for_spec(teams["free"])
                self.team_placement(self._players[0], "spectator", True)
                teams.remove(self._players[0])
                free -= 1
            return True
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue fix_free Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def get_ratings(self, p1, p2, teams):
        bdm = self.get_cvar("qlx_queueUseRating", bool)
        red_rating = self.team_average(teams["red"], bdm)
        blue_rating = self.team_average(teams["blue"], bdm)
        p1_rating = self.get_rating(p1, bdm)
        p2_rating = self.get_rating(p2, bdm)
        return red_rating, blue_rating, p1_rating, p2_rating

    def team_average(self, team, bdm=True):
        try:
            """Calculates the average rating of a team."""
            avg = 0
            if team:
                for p in team:
                    r = self.get_rating(p.steam_id, bdm)
                    avg += r
                avg /= len(team)
            return int(round(avg))
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue team average Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def get_rating(self, sid, bdm=True):
        if bdm:
            return self.get_bdm_rating(sid)
        else:
            return self.get_elo_rating(sid)

    def get_gametype(self):
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self.q_game_info[0]
        return game_type

    def get_bdm_rating(self, sid):
        try:
            game_type = self.get_gametype()
            if self.db.exists(BDM_KEY.format(sid, game_type, "rating")):
                try:
                    rating = self.db.get(BDM_KEY.format(sid, game_type, "rating"))
                    rating = int(float(rating))
                except ValueError or TypeError:
                    rating = 0
            else:
                rating = 0
            if rating == 0:
                rating = self.get_cvar("qlx_bdmDefaultBDM", int)
                if not rating or not isinstance(rating, int):
                    rating = 1022
            return rating
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue get BDM rating Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def get_elo_rating(self, sid):
        try:
            game_type = self.get_gametype()
            rating = 0
            sid = str(sid)
            with self.elo_lock:
                if sid in self.elo_ratings and game_type in self.elo_ratings[sid]:
                    rating = self.elo_ratings[sid][game_type]
            if rating == 0 and self.db.exists(ELO_KEY.format(sid, self.get_gametype())):
                try:
                    rating = int(float(self.db.get(ELO_KEY.format(sid, game_type))))
                    if rating == DEFAULT_ELO:
                        self.request_elo_rating(sid)
                except (ValueError, TypeError):
                    rating = 0
            if rating == 0:
                rating = DEFAULT_ELO
                self.request_elo_rating(sid)
            return rating
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue get ELO rating Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    @minqlx.thread
    def request_elo_rating(self, sid):
        if self.retrieving_elo or not sid:
            return
        self.retrieving_elo = True
        if ENABLE_LOG:
            self.queue_log.info("Requesting ELO rating information from {} for: {}".format(ELO_URL, sid))
        try:
            if type(sid) == list:
                sid = '+'.join(str(x) for x in sid)
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
                else:
                    time.sleep(0.1)
            if response:
                elo_dict[sid] = {}
                now = int(time.time())
                save_db = self.get_cvar("qlx_queueSaveEloToDatabase", bool)
                with self.elo_lock:
                    for record in info_js["players"]:
                        p_sid = record['steamid']
                        if p_sid not in self.elo_ratings:
                            self.elo_ratings[p_sid] = {}
                        self.elo_ratings[p_sid]['time'] = now
                        for gt in SUPPORTED_GAMETYPES:
                            if gt in record:
                                elo = record[gt]["elo"]
                                if save_db:
                                    self.db.set(ELO_KEY.format(p_sid, gt), elo)
                                self.elo_ratings[p_sid][gt] = elo
                            else:
                                try:
                                    del self.elo_ratings[p_sid][gt]
                                except KeyError:
                                    pass
                    if ENABLE_LOG:
                        self.queue_log.info("ELO ratings: {}".format(self.elo_ratings))
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue request_elo_rating Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))
        finally:
            self.retrieving_elo = False

    @minqlx.next_frame
    def team_placement(self, player, team, add_queue=False):
        if ENABLE_LOG:
            self.queue_log.info("specqueue team placement: {} put on team {}".format(player, team))
        try:
            player.put(team)
            if add_queue:
                self.add_to_queue_pos(player, 0)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue team placement Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    @minqlx.thread
    def add_join_times(self):
        try:
            teams = self.teams()
            for player in teams["red"] + teams["blue"] + teams["free"]:
                self._join.add_to_times(player.steam_id)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue add join times Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    @minqlx.thread
    def record_player_models(self):
        try:
            for player in self.players():
                try:
                    model = player.model
                except KeyError:
                    model = "sarge"
                except Exception as e:
                    model = "sarge"
                    if ENABLE_LOG:
                        self.queue_log.info("specqueue get_player_model Exception: {}\n{}"
                                            .format(type(e).__name__, traceback.format_exc()))
                self._player_models[player.id] = model
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue record_player_models Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def add_to_join(self, player):
        try:
            self._join.add_to_times(player.steam_id)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue add to join Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def remove_from_join(self, player):
        try:
            self._join.remove_from_times(player.steam_id)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue remove from join Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def get_join_time(self, player):
        try:
            if str(player.steam_id) not in self._join:
                self.add_to_join(player)
                return time.time()
            return self._join.get_time(player.steam_id)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue get join time Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def get_join_times(self):
        try:
            return self._join.times()
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue get join times Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    @minqlx.thread
    def look_at_teams(self, delay=None):
        try:
            if self.game and self.game.state in ["in_progress", "countdown"] and\
                    self.q_game_info[0] in TEAM_BASED_GAMETYPES:
                if delay:
                    time.sleep(delay)
                teams = self.teams()
                difference = len(teams["red"]) - len(teams["blue"])
                abs_diff = abs(difference)
                if abs_diff == 1 and not self.get_cvar("qlx_queueEnforceEvenTeams", bool):
                    return
                if abs_diff > 0 and self._latch_ignore or self._ignore:
                    if not self._ignore_msg_already_said:
                        self.msg("^6Uneven teams action^7: no action will be taken due to admin setting!")
                        self._ignore_msg_already_said = True
                    return
                p_count = len(teams["red"]) + len(teams["blue"])
                players = []
                move_players = []
                where = None
                spec_player = None

                if abs_diff > 0 and self._specPlayer[7] <= p_count <= self._specPlayer[8]:
                    if difference == -1:
                        self.get_player_for_spec(teams["blue"].copy())
                        spec_player = self._players[0]
                    elif difference == 1:
                        self.get_player_for_spec(teams["red"].copy())
                        spec_player = self._players[0]
                    else:
                        move = int(abs_diff / 2)
                        if (difference % 2) == 0:
                            spec = 0
                        else:
                            spec = 1
                        if difference < 0:
                            self.get_uneven_players(teams["blue"].copy(), move + spec)
                            where = "red"
                        else:
                            self.get_uneven_players(teams["red"].copy(), move + spec)
                            where = "blue"
                        if (difference % 2) != 0:
                            spec_player = self._players[0]
                            self._players.pop(0)
                        for p in self._players:
                            players.append(p.name)
                            move_players.append(p)
                    if not delay:
                        if len(move_players) > 0:
                            self.msg("^3Uneven Teams Detected^7: {} ^7will be moved to {}^7."
                                     .format("^7, ".join(players), where))
                        if spec_player:
                            self.msg("^3Uneven Teams Detected^7: {} ^7will be moved to ^3spectate^7."
                                     .format(spec_player))
                if delay:
                    if len(players) > 0:
                        self.msg("^3Uneven Teams Detected^7: {} ^7will be moved to {}^7."
                                 .format("^7, ".join(players), where))
                        self.even_the_teams(False)
                    elif spec_player:
                        self.msg("^3Uneven Teams Detected^7: {} ^7will be moved to ^3spectate ^7if not fixed."
                                 .format(spec_player))
                        self.msg("^2Looking at teams again in {} seconds to assess even status."
                                 .format(self._specPlayer[9]))
                        time.sleep(self._specPlayer[9])
                        self.even_the_teams(False)
                else:
                    self.even_the_teams(True)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue look at teams Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    @minqlx.thread
    def even_the_teams(self, delay=False):
        if not self.get_cvar("qlx_queueEnforceEvenTeams", bool):
            return
        try:
            if self.game and self.game.state in ["in_progress", "countdown"] and\
                    self.q_game_info[0] in TEAM_BASED_GAMETYPES:
                if delay:
                    if self.game.type_short == "ft":
                        countdown = self._specPlayer[5]
                    else:
                        countdown = self._specPlayer[6]
                    time.sleep(max(countdown / 1000 - 0.3, 0))

                teams = self.teams()
                difference = len(teams["red"]) - len(teams["blue"])
                if abs(difference) > 0 and self._latch_ignore or self._ignore:
                    if not self._ignore_msg_already_said:
                        self.msg("^6Uneven teams action^7: no action will be taken due to admin setting!")
                        self._ignore_msg_already_said = True
                    return
                p_count = len(teams["red"] + teams["blue"])
                players = []
                move_players = []
                where = None
                spec_player = None

                if abs(difference) > 0 and self._specPlayer[3] <= p_count <= self._specPlayer[4]:
                    if difference == -1:
                        self.get_player_for_spec(teams["blue"])
                        spec_player = self._players[0]
                        if ENABLE_LOG:
                            self.queue_log.info("Spectating: {}, Settings: {} {} {}"
                                                .format(spec_player, self.get_cvar("qlx_queueSpecByTime"),
                                                        self.get_cvar("qlx_queueSpecByScore"),
                                                        self.get_cvar("qlx_queueSpecByPrimary")))
                    elif difference == 1:
                        self.get_player_for_spec(teams["red"])
                        spec_player = self._players[0]
                        if ENABLE_LOG:
                            self.queue_log.info("Spectating: {}, Settings: {} {} {}"
                                                .format(spec_player, self.get_cvar("qlx_queueSpecByTime"),
                                                        self.get_cvar("qlx_queueSpecByScore"),
                                                        self.get_cvar("qlx_queueSpecByPrimary")))
                    else:
                        move = int(abs(difference) / 2)
                        if (difference % 2) == 0:
                            spec = 0
                        else:
                            spec = 1
                        if difference < 0:
                            self.get_uneven_players(teams["blue"].copy(), move + spec)
                            where = "red"
                        else:
                            self.get_uneven_players(teams["red"].copy(), move + spec)
                            where = "blue"
                        if (difference % 2) != 0:
                            spec_player = self._players[0]
                            self._players.pop(0)
                        for p in self._players:
                            players.append(p.name)
                            move_players.append(p)
                    if len(move_players) > 0:
                        for player in move_players:
                            self.team_placement(player, where)
                        self.msg("^3Uneven Teams Detected^7: {} ^7was moved to {}^7."
                                 .format("^7, ".join(players), where))
                    if spec_player:
                        self.uneven_teams_move_to_spec[spec_player.steam_id] = True
                        self.team_placement(spec_player, "spectator", True)
                        self.msg("^3Uneven Teams Detected^7: {} ^7was moved to ^3spectate^7.".format(spec_player))
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue even the teams Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def get_cvars(self):
        self._specPlayer = [self.get_cvar("qlx_queueSpecByTime", bool), self.get_cvar("qlx_queueSpecByScore", bool),
                            True if self.get_cvar("qlx_queueSpecByPrimary").lower() == "score" else False,
                            self.get_cvar("qlx_queueMinPlayers", int), self.get_cvar("qlx_queueMaxPlayers", int),
                            self.get_cvar("g_freezeRoundDelay", int), self.get_cvar("g_roundWarmupDelay", int),
                            self.get_cvar("qlx_queueMinPlayers", int), self.get_cvar("qlx_queueMaxPlayers", int),
                            self.get_cvar("qlx_queueCheckTeamsDelay", int)]

    # Finds the player, that meets the set criteria, to move to spectate and returns that player
    # Does not start its own thread
    def get_player_for_spec(self, team):
        try:
            t_players = []
            s_players = []
            lowest_time = 0
            lowest_score = 999
            for player in team.copy():
                try:
                    player.update()
                except minqlx.NonexistentPlayerError:
                    continue
                p_time = self.get_join_time(player)
                if p_time > lowest_time:
                    lowest_time = p_time
                    t_players = [player]
                elif p_time == lowest_time:
                    t_players.append(player)
                p_score = player.stats.score
                if p_score < lowest_score:
                    lowest_score = p_score
                    s_players = [player]
                elif p_score == lowest_score:
                    s_players.append(player)
            if self.game.state == "in_progress":
                if self._specPlayer[0] and self._specPlayer[1]:
                    if self._specPlayer[2]:
                        if len(s_players) > 1:
                            lowest_time = 0
                            temp_player = s_players[0]
                            for player in s_players:
                                if self.get_join_time(player) > lowest_time:
                                    temp_player = player
                            self._players = [temp_player]
                        else:
                            self._players = [s_players[0]]
                    else:
                        if len(t_players) > 1:
                            lowest_score = 999
                            temp_player = t_players[0]
                            for player in t_players:
                                if player.stats.score < lowest_score:
                                    temp_player = player
                            self._players = [temp_player]
                        else:
                            self._players = [t_players[0]]
                elif self._specPlayer[1]:
                    self._players = [s_players[randrange(len(s_players))]]
                else:
                    self._players = [t_players[randrange(len(t_players))]]
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue get player for spec Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    # Function meant to return the player that would be sent to spectate because
    #  the get_player_for_spec function does not return anything
    # Does not start its own thread
    def return_spec_player(self, team):
        try:
            self.get_player_for_spec(team)
            return [self._players[0]]
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue return spec player Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def get_spec(self, player, msg, channel):
        @minqlx.thread
        def get_player():
            teams = self.teams().copy()
            if self.game.state == "in_progress":
                difference = len(teams["red"]) - len(teams["blue"])
                if difference:
                    team = teams["red"] if difference > 0 else teams["blue"]
                else:
                    team = teams["red"] + teams["blue"]
                spec_player = self.return_spec_player(team)[0]
            else:
                spec_player = self.return_spec_player(teams["red"] + teams["blue"])[0]
            if ENABLE_LOG:
                self.queue_log.info("Player to Spectate: ^7{}".format(spec_player))

        get_player()

    @minqlx.thread
    def get_uneven_players(self, team, amount):
        try:
            t_players = {}
            s_players = {}
            self._players = []
            for player in team:
                t_players[str(self.get_join_time(player))] = player
                s_players[str(player.stats.score)] = player

            if self._specPlayer[0] and self._specPlayer[1]:
                if self._specPlayer[2]:
                    sorted_players = sorted(((k, v) for k, v in s_players.items()), reverse=False)
                else:
                    sorted_players = sorted(((k, v) for k, v in t_players.items()), reverse=True)
            elif self._specPlayer[1]:
                sorted_players = sorted(((k, v) for k, v in s_players.items()), reverse=False)
            else:
                sorted_players = sorted(((k, v) for k, v in t_players.items()), reverse=True)
            count = 0
            for s, player in sorted_players:
                self._players.append(player)
                count += 1
                if count == amount:
                    break
            return
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue get uneven players Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    @minqlx.thread
    def check_spec_time(self):
        time.sleep(5)
        try:
            max_spec_time = self.get_cvar("qlx_queueMaxSpecTime", int)
            if 0 < max_spec_time < 9998:
                admin = self.get_cvar("qlx_queueAdmin", int)
                admin_multiplier = self.get_cvar("qlx_queueAdminSpec", int)
                spectators = self.teams()["spectator"]
                if self._spec.count > 0 and len(spectators) > 0:
                    s = self._spec.times()
                    for p, t in s.items():
                        spec = self.player(int(p))
                        permission = self.db.get_permission(int(p))
                        if spec in spectators:
                            time_in_spec = round((time.time() - t)) / 60
                            if permission >= admin:
                                if admin_multiplier:
                                    if time_in_spec >= max_spec_time * admin_multiplier:
                                        spec.kick("was in spectate, not the queue, for too long.")
                            elif time_in_spec >= max_spec_time:
                                spec.kick("was in spectate, not the queue, for too long.")
                        else:
                            self.remove_from_spec(spec)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue check spec time Exception:{} {}"
                                    .format(type(e).__name__, traceback.format_exc()))

    # Search for a player name match using the supplied string
    def find_player(self, name):
        try:
            found_player = None
            found_count = 0
            if name.isdigit():
                _id = int(name)
                for player in self.players():
                    if player.id == _id or player.steam_id == _id:
                        found_player = player
                        return found_player, int(str([found_player]).split(":")[0].split("(")[1])
            else:
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
                self.queue_log.info("specqueue find_player Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def player_in_queue(self, player):
        if player in self._queue:
            return self._queue.get_queue_position(player)
        else:
            return None

    # ==============================================
    #               Minqlx Bot Commands
    # ==============================================
    def get_current_settings(self, player, msg, channel):
        try:
            message = ["^6SpecQueue current variable states:"]
            if self._queue:
                message.append("^3Queue: {} Size: {}".format(str(self._queue.players()), self._queue.count))
            else:
                message.append("^3Queue is empty")
            if self._spec.count > 0:
                message.append("^3Specs: {} Size: {}".format(str(self._spec.times()), self._spec.count))
            else:
                message.append("^3Specs is empty")
            if self._join.count > 0:
                message.append("^3Join Times: {} Size: {}".format(str(self._join.times()), self._join.count))
            else:
                message.append("^3Join Times is empty")
            if len(self._player_models) > 0:
                message.append("^3Player Models^7: {}".format(str(self._player_models)))
            else:
                message.append("^3Player Models is empty")
            message.append("^1Red Locked^7: {}^7, ^4Blue Locked^7: {}^7, ^2Free Locked^7: {}"
                           .format("^5True" if self.red_locked else "^6False",
                                   "^5True" if self.blue_locked else "^6False",
                                   "^5True" if self.free_locked else "^6False"))
            message.append("^3End Screen status^7: {}".format("^5True" if self.end_screen else "^6False"))
            message.append("^3Displaying status^7- ^2Queue {}^7, ^4Spec {}"
                           .format("^5True" if self.displaying_queue else "^6False",
                                   "^5True" if self.displaying_spec else "^6False"))
            message.append("^3In Countdown^7: {}".format("^5True" if self.in_countdown else "^6False"))
            message.append("^3Game Info^7: {}".format(self.q_game_info))
            message.append("^3Ignore Status^7: {} ^3Latch^7: {}"
                           .format("^5True" if self._ignore else "^6False",
                                   "^5True" if self._latch_ignore else "^6False"))
            if self.get_cvar("qlx_queueUseSkillPlacement", bool):
                message.append("^3Players are being placed using {} rankings."
                               .format("BDM" if self.get_cvar("qlx_queueUseRating", bool) else "ELO"))
            else:
                message.append("^3Players are not being placed using rankings.")
            if channel != "console":
                player.tell("\n".join(message))
            minqlx.console_print(message[0])
            minqlx.console_print(message[1])
            minqlx.console_print(message[2])
            minqlx.console_print(message[3])
            minqlx.console_print(message[4])
            minqlx.console_print(" ".join(message[5:8]))
            minqlx.console_print(" ".join(message[8:11]))
            minqlx.console_print(message[11])
            return minqlx.RET_STOP_ALL
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue get_current_settings Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def reset_queue(self, player, msg, channel):
        try:
            minqlx.console_command("unlock red")
            minqlx.console_command("unlock blue")
            minqlx.console_command("unlock free")
            if self.red_locked:
                self.red_locked = False
            if self.blue_locked:
                self.blue_locked = False
            if self.free_locked:
                self.free_locked = False
            if self.end_screen:
                self.end_screen = False
            if self.in_countdown:
                self.in_countdown = False
            if self.displaying_queue:
                self.displaying_queue = False
            if self.displaying_spec:
                self.displaying_spec = False
            if self._ignore:
                self._ignore = False
            if self._latch_ignore:
                self._latch_ignore = False
            self.check_for_opening(0.2)
            specs = self.teams()["spectator"]
            if len(specs):
                for player in specs:
                    player.tell("^1The queue statuses have been reset. Check your position in the queue.")
            return minqlx.RET_STOP_ALL
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue reset_queue Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    @minqlx.thread
    def reset_players_model(self, msg=None):
        try:
            sleep = msg if msg else 0.2
            time.sleep(sleep)
            players = self.players().copy()
            for pid, model in self._player_models.items():
                try:
                    player = self.player(pid)
                except minqlx.NonexistentPlayerError:
                    continue
                count = len(players)
                while count > 0:
                    count -= 1
                    if players[count].id == pid:
                        del players[count]
                        break
                player.model = model
            for pl in players:
                if pl.model:
                    pl.model = pl.model
                else:
                    pl.model = "sarge"
            return True
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue reset_players_model Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def reset_model(self, player=None, msg=None, channel=None):
        try:
            if len(msg) > 1:
                if msg[1] == "all":
                    self.reset_players_model()
                    player.tell("^3Player models have been reset")
                    return minqlx.RET_STOP_ALL
                else:
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
            if player.id in self._player_models:
                player.model = self._player_models[player.id]
            elif player.model:
                player.model = player.model
            else:
                player.model = "sarge"
            return
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue reset_model Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def ignore_imbalance(self, player, msg, channel):
        try:
            self.msg("^3The move to ^1spectate ^3action will be ignored this round")
            self._ignore = True
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue ignore imbalance Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def ignore_imbalance_latch(self, player, msg, channel):
        try:
            if len(msg) < 2:
                player.tell("^3Command must include 'ignore', 'spec', or 'setting'")
                return minqlx.RET_STOP_ALL
            else:
                setting = msg[1].lower()
                if setting == "ignore":
                    self.msg("^3The move to spectate actions will be ^1ignored ^3until ^4re-enabled")
                    self._latch_ignore = True
                elif setting == "spec" or setting == "spectate":
                    self.msg("^3The move to spectate actions have been ^4re-enabled")
                    self._latch_ignore = False
                elif setting == "setting" or setting == "set":
                    self.msg("^3The move to ^1spectate ^3actions are set to {}"
                             .format("ignore" if self._latch_ignore else "spectate"))
                else:
                    player.tell("^3Command must include 'ignore', 'spec', or 'setting'")
                    return minqlx.RET_STOP_ALL
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue ignore imbalance latch Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def cmd_queue_add(self, player, msg, channel):
        try:
            if len(msg) < 2:
                self.add_to_queue(player)
            elif self.db.has_permission(player.steam_id, self.get_cvar("qlx_queueAdmin", int)):
                try:
                    i = int(msg[1])
                    target_player = self.player(i)
                    if not (0 <= i < 64) or not target_player:
                        raise ValueError
                except ValueError:
                    player.tell("Invalid ID.")
                    return
                except minqlx.NonexistentPlayerError:
                    player.tell("Invalid client ID.")
                    return
                except Exception as e:
                    if ENABLE_LOG:
                        self.queue_log.info("specqueue Cmd Que Add Exception: {}\n{}"
                                            .format(type(e).__name__, traceback.format_exc()))
                    return
                if len(msg) > 2:
                    try:
                        pos = int(msg[2])
                        self.add_to_queue_pos(target_player, pos)
                    except ValueError:
                        self.add_to_queue(target_player)
                else:
                    self.add_to_queue(target_player)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue cmd queue add Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))
        self.update_queue_tags()
        self.check_for_opening(0.2)

    def cmd_qversion(self, player, msg, channel):
        channel.reply("^7This server has installed ^2{0} version {1} by BarelyMiSSeD\n"
                      "https://github.com/BarelyMiSSeD/minqlx-plugins/{0}.py"
                      .format(self.__class__.__name__, VERSION))

    def cmd_list_queue(self, player=None, msg=None, channel=None):
        self.exec_list_queue(player, msg, channel)

    @minqlx.thread
    def exec_list_queue(self, player=None, msg=None, channel=None):
        try:
            spectators = self.teams()["spectator"]
            count = 0
            message = []
            if self._queue and len(spectators) > 0:
                for n in range(0, self._queue.count):
                    sid = self._queue[n]
                    p = self.player(sid)
                    if p in spectators:
                        t = self._queue[str(sid)]
                        time_in_queue = round((time.time() - t))
                        if time_in_queue / 60 > 1:
                            queue_time = "^7{}^4m^7:{}^4s^7".format(int(time_in_queue / 60), time_in_queue % 60)
                        else:
                            queue_time = "^7{}^4s^7".format(time_in_queue)
                        message.append("{} ^7[{}] ^7{}".format(p, count + 1, queue_time))
                        count += 1
                    else:
                        self.remove_from_queue(p)
            else:
                self._queue.empty_queue()
            if count == 0:
                message = ["^4No one is in the queue."]
            if channel:
                channel.reply("^2Queue^7: " + ", ".join(message))
            elif player or count:
                self.msg("^2Queue^7: " + ", ".join(message))
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue cmd list queue Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def cmd_list_specs(self, player=None, msg=None, channel=None):
        self.exec_list_specs(player, msg, channel)

    @minqlx.thread
    def exec_list_specs(self, player=None, msg=None, channel=None):
        try:
            spectators = self.teams()["spectator"]
            count = 0
            message = []
            if self._spec and len(spectators) > 0:
                s = self._spec.times()
                for p, t in s.items():
                    spec = self.player(int(p))
                    if spec in spectators:
                        time_in_spec = round((time.time() - t))
                        if time_in_spec / 60 > 1:
                            spec_time = "^7{}^4m^7:{}^4s^7".format(int(time_in_spec / 60), time_in_spec % 60)
                        else:
                            spec_time = "^7{}^4s^7".format(time_in_spec)
                        message.append("{} ^7{}".format(spec, spec_time))
                        count += 1
                    else:
                        self.remove_from_spec(spec)
            if count == 0:
                message = ["^4No one is set to spectate only."]
            if channel:
                channel.reply("^4Spectators^7: " + ", ".join(message))
            elif player or count:
                self.msg("^4Spectators^7: " + ", ".join(message))
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue exec list specs Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def specqueue_version(self):
        return VERSION

    def cmd_go_afk(self, player=None, msg=None, channel=None):
        if len(msg) > 1:
            if self.db.get_permission(player.steam_id) >= self.get_cvar("qlx_queueAdmin", int):
                match = self.find_player(msg[1])
                self.exec_go_afk(match[0], msg[0][1:])
        else:
            self.exec_go_afk(player, msg[0][1:])

    @minqlx.thread
    def exec_go_afk(self, player, afk_tag):
        try:
            if player.team != "spectator":
                self.team_placement(player, "spectator")
                if not self.end_screen:
                    self.check_for_opening(0.2)
                    if self.q_game_info[0] in NO_COUNTDOWN_TEAM_GAMES and \
                            not (self.red_locked or self.blue_locked or self.free_locked):
                        self.look_at_teams(1.0)
            self.remove_from_queue(player)
            self.add_to_spec(player)
            self.remove_from_join(player)
            self.add_to_afk(player, afk_tag)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue exec_go_afk Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def cmd_here(self, player=None, msg=None, channel=None):
        self.exec_here(player)

    @minqlx.thread
    def exec_here(self, player):
        try:
            if player.team == "spectator":
                if not self.end_screen:
                    self.check_for_opening(0.2)
                    if self.q_game_info[0] in NO_COUNTDOWN_TEAM_GAMES and \
                            not (self.red_locked or self.blue_locked or self.free_locked):
                        self.look_at_teams(1.0)
                self.add_to_spec(player)
                self.remove_from_join(player)
            self.remove_from_afk(player)
            self.remove_from_queue(player)
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue exec_here Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def add_to_afk(self, player, afk_tag):
        try:
            self._afk.add_to_times(player.steam_id)
            player.center_print("^6AFK Mode\n^7Type ^4!here ^7when back.")
            self._afk_tag[str(player.steam_id)] = afk_tag
            player.clan = player.clan
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue add_to_afk Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def remove_from_afk(self, player, msg=True):
        try:
            sid = player.steam_id
            if str(sid) in self._afk:
                self._afk.remove_from_times(sid)
                if msg:
                    player.center_print("^3Not marked AFK\n^7Join to play or enter the queue.")
                    player.clan = player.clan
            if str(sid) in self._afk_tag:
                del self._afk_tag[str(sid)]
        except Exception as e:
            if ENABLE_LOG:
                self.queue_log.info("specqueue remove_from_afk Exception: {}\n{}"
                                    .format(type(e).__name__, traceback.format_exc()))

    def cmd_tags(self, player=None, msg=None, channel=None):
        if self._queue_tags:
            player.tell("^3Allowed spectator tags are: ^6{}".format("^7, ^6".join(SPEC_TAGS)))
        else:
            player.tell("^3Spectator tags are not being monitored")
