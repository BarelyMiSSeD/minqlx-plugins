# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# This is a queueing plugin for the minqlx admin bot.
# This plugin requires the server to be using the serverBDM.py plugin

# This is a queueing plugin for the minqlx admin bot.
# This plugin requires the server to be using the serverBDM.py plugin
#
# This plugin is intended to help keep the game as enjoyable as possible,
# without the hassles of people making teams uneven, or someone joining later than others,
# but happening to hit the join button first and cutting in line when a play spot opens.
#
# The plugin will also attempt to keep team games even, when adding 2 players at once,
# by putting players into the most appropriate team, based on team scores or player BDMs.
#
# This plugin will spectate people when teams are uneven. It will, by default settings,
# first look at player score then player play time to determine who, on the team with more players,
# gets put to spectate. When a player gets put to spectate they will automatically get put into the
# queue in the beginning of the line.
#
# There is also the option to have the players in spectate for too long (set with qlx_queueMaxSpecTime)
# to be kicked. This will only kick the player, not do any kind of ban, so the player can reconnect immediately.
# This feature will not kick people with permission levels at or above the qlx_queueAdmin level,
# or people who are in the queue.

"""
//set the minqlx permission level needed to admin this script
set qlx_queueAdmin", "3"
//The script will try to place players in by BDM ranking, if this is set on (0=off 1=on) it will
// put the higher BDM player in the losing team if the score is greater than the qlx_queueTeamScoresDiff setting
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
set qlx_queueSpecByPrimary "score"
//set to an amount of minutes a player is allowed to remain in spectate (while not in the queue) before the server will
// kick the player to make room for people who want to play. (valid values are greater than "0" and less than "9999")
set qlx_queueMaxSpecTime "9999"
"""

import minqlx
import time
from threading import RLock
from random import randint

VERSION = "2.03.14"
TEAM_BASED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "ad", "1f", "har")
NO_COUNTDOWN_TEAM_GAMES = ("ft", "1f", "ad", "dom", "ctf")
NONTEAM_BASED_GAMETYPES = ("ffa", "race", "rr")
BDM_GAMETYPES = ("ft", "ca", "ctf", "ffa", "ictf", "tdm")
NON_ROUND_BASED_GAMETYPES = ("ffa", "race", "tdm", "ctf", "har", "dom", "rr")
BDM_KEY = "minqlx:players:{}:bdm:{}:{}"


class JoinTime:
    def __init__(self):
        self.join_times = {}
        self.count = 0
        self.rlock = RLock()

    def __contains__(self, player):
        return player in self.join_times

    def add_to_jt(self, player):
        with self.rlock:
            if player not in self.join_times:
                self.join_times[player] = time.time()
                self.count += 1

    def remove_from_jt(self, player):
        if self.count > 0:
            with self.rlock:
                if player in self.join_times:
                    del self.join_times[player]
                    self.count -= 1

    def get_join_time(self, player):
        if player in self.join_times:
            return self.join_times[player]
        else:
            return None

    def size(self):
        return self.count

    def get_jt(self):
        with self.rlock:
            return self.join_times.copy()


class Spectators:
    def __init__(self):
        self.spectators = {}
        self.count = 0
        self.rlock = RLock()

    def __contains__(self, player):
        return player in self.spectators

    def add_to_spec(self, player):
        with self.rlock:
            if player not in self.spectators:
                self.spectators[player] = time.time()
                self.count += 1

    def remove_from_spec(self, player):
        if self.count > 0:
            with self.rlock:
                if player in self.spectators:
                    del self.spectators[player]
                    self.count -= 1

    def size(self):
        return self.count

    def get_spectators(self):
        with self.rlock:
            return self.spectators.copy()


class PlayerQueue:
    def __init__(self):
        self.queue = []
        self.queue_player = []
        self.queue_time = {}
        self.count = 0
        self.rlock = RLock()

    def __contains__(self, player):
        return player in self.queue or player in self.queue_player

    def __getitem__(self, index):
        return [self.queue[index], self.queue_player[index]]

    def add_to_queue(self, sid, player):
        with self.rlock:
            added = 0
            if sid not in self.queue:
                self.queue.append(sid)
                self.queue_player.append(player)
                added = 1
                self.count += 1
                self.queue_time[str(sid)] = time.time()
            return added

    def add_to_queue_pos(self, sid, player, pos):
        with self.rlock:
            added = 0
            if sid not in self.queue:
                self.queue.insert(pos, sid)
                self.queue_player.insert(pos, player)
                added = 2
                self.count += 1
                self.queue_time[str(sid)] = time.time()
            return added

    def next(self):
        return [self.queue[0], self.queue_player[0]]

    def get_next(self):
        return self.get_from_queue()

    def get_from_queue(self, pos=None):
        if self.count > 0:
            with self.rlock:
                self.count -= 1
                if pos:
                    if pos == -1:
                        sid = self.queue.pop()
                        player = self.queue_player.pop()
                    else:
                        sid = self.queue.pop(pos)
                        player = self.queue_player.pop(pos)
                else:
                    sid = self.queue.pop(0)
                    player = self.queue_player.pop(0)
                del self.queue_time[str(sid)]
                return [sid, player]

    def get_two_from_queue(self):
        if self.count > 1:
            with self.rlock:
                self.count -= 2
                sid1 = self.queue.pop(0)
                player1 = self.queue_player.pop(0)
                del self.queue_time[str(sid1)]
                sid2 = self.queue.pop(0)
                player2 = self.queue_player.pop(0)
                del self.queue_time[str(sid2)]
                return [sid1, player1, sid2, player2]

    def remove_from_queue(self, sid, player):
        if self.count > 0:
            with self.rlock:
                if sid in self.queue:
                    self.count -= 1
                    self.queue.remove(sid)
                    self.queue_player.remove(player)
                    del self.queue_time[str(sid)]

    def get_queue_time(self, sid):
        if str(sid) in self.queue_time:
            return self.queue_time[str(sid)]
        else:
            return None

    def get_queue_position(self, player):
        if player in self.queue:
            return self.queue.index(player)
        if player in self.queue_player:
            return self.queue_player.index(player)
        else:
            return -1

    def get_queue(self):
        with self.rlock:
            return self.queue.copy()

    def get_queue_names(self):
        with self.rlock:
            return self.queue_player.copy()

    def size(self):
        return self.count

    def clear(self):
        self.queue = []
        self.queue_player = []
        self.queue_time = {}
        self.count = 0


class specqueue(minqlx.Plugin):
    def __init__(self):
        # queue cvars
        self.set_cvar_once("qlx_queueAdmin", "3")
        self.set_cvar_once("qlx_queuePlaceByTeamScores", "1")
        self.set_cvar_once("qlx_queueTeamScoresDiff", "3")
        self.set_cvar_once("qlx_queueQueueMsg", "1")
        self.set_cvar_once("qlx_queueSpecMsg", "1")
        self.set_cvar_once("qlx_queueMinPlayers", "2")
        self.set_cvar_once("qlx_queueMaxPlayers", "30")
        self.set_cvar_once("qlx_queueSpecByTime", "1")
        self.set_cvar_once("qlx_queueSpecByScore", "1")
        self.set_cvar_once("qlx_queueSpecByPrimary", "score")
        self.set_cvar_once("qlx_queueMaxSpecTime", "9999")  # time in minutes

        # Minqlx bot Hooks
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("game_start", self.handle_game_start)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("round_countdown", self.handle_round_countdown)
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("round_end", self.handle_round_end)
        self.add_hook("death", self.death_monitor)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("team_switch_attempt", self.handle_team_switch_attempt)
        self.add_hook("set_configstring", self.handle_set_configstring)
        self.add_hook("client_command", self.handle_client_command)
        self.add_hook("vote_ended", self.handle_vote_ended)
        self.add_hook("console_print", self.handle_console_print)
        self.add_hook("map", self.handle_map)

        # Minqlx bot commands
        self.add_command(("q", "queue"), self.cmd_list_queue)
        self.add_command(("s", "specs"), self.cmd_list_specs)
        self.add_command(("addqueue", "addq"), self.cmd_queue_add)
        self.add_command(("qversion", "qv"), self.cmd_qversion)

        self.add_command("ignore", self.ignore_imbalance, 3)
        self.add_command("latch", self.ignore_imbalance_latch, 3)

        # Script Variables, Lists, and Dictionaries
        self.rlock = RLock()
        self._queue = PlayerQueue()
        self._spec = Spectators()
        self._join = JoinTime()
        self._players = []
        self.red_locked = False
        self.blue_locked = False
        self.end_screen = False
        self.displaying_queue = False
        self.displaying_spec = False
        self.in_countdown = False
        self.death_count = 0
        self.q_gameinfo = [self.game.type_short, self.get_cvar("teamsize", int), self.get_cvar("fraglimit", int)]
        self.checking_space = False
        self._round = 0

        # Initialize Commands
        self.add_spectators()
        self.add_join_times()

        self._ignore = False
        self._latch_ignore = False
        self._ignore_msg_already_said = False

    # ==============================================
    #               Event Handler's
    # ==============================================

    def handle_player_disconnect(self, player, reason):
        self.remove_from_spec(player)
        self.remove_from_queue(player)
        self.remove_from_join(player)
        self.check_for_opening(0.5)

    def handle_team_switch(self, player, old_team, new_team):
        if new_team != "spectator":
            self.remove_from_spec(player)
            self.remove_from_queue(player)
            if player.steam_id not in self._join:
                self.add_to_join(player)
        else:
            if not self.end_screen:
                self.check_for_opening(0.2)

            @minqlx.delay(1)
            def check_spectator():
                if player.steam_id not in self._queue:
                    self.add_to_spec(player)
                self.remove_from_join(player)

            check_spectator()

    def handle_team_switch_attempt(self, player, old_team, new_team):
        if new_team != "spectator" and old_team == "spectator":
            if self.q_gameinfo[0] in TEAM_BASED_GAMETYPES:
                teams = self.teams()
                if len(teams["red"]) + len(teams["blue"]) >= self.get_max_players()\
                        or self.game.state in ["in_progress", "countdown"] or\
                        self._queue.size() > 0 or self.red_locked or self.blue_locked:
                    if player.steam_id not in self._join:
                        self.add_to_join(player)
                    self.add_to_queue(player)
                    self.remove_from_spec(player)
                    self.check_for_opening(0.2)
                    return minqlx.RET_STOP_ALL
            elif self.q_gameinfo[0] in NONTEAM_BASED_GAMETYPES:
                if len(self.teams()["free"]) >= self.get_max_players()\
                        or self.game.state in ["in_progress", "countdown"] or self._queue.size() > 0:
                    if player.steam_id not in self._join:
                        self.add_to_join(player)
                    self.add_to_queue(player)
                    self.remove_from_spec(player)
                    self.check_for_opening(0.2)
                    return minqlx.RET_STOP_ALL

    def handle_set_configstring(self, index, values):
        args = values.split("\\")[1:]
        if "teamsize" in args:
            teamsize = args[args.index("teamsize") + 1]
            if self.q_gameinfo[1] != teamsize:
                self.q_gameinfo[1] = teamsize
                self.check_for_opening(1.5)
        if "fraglimit" in args:
            fraglimit = args[args.index("fraglimit") + 1]
            self.q_gameinfo[2] = fraglimit

    def handle_client_command(self, player, command):
        if command == "team s" and player in self.teams()["spectator"]:
            self.add_to_spec(player)
            self.remove_from_queue(player)
            self.remove_from_join(player)
            player.center_print("^6You are set to spectate only")

    def handle_new_game(self):
        self.end_screen = False
        self.red_locked = False
        self.blue_locked = False
        self.displaying_queue = False
        self.displaying_spec = False

        if self.q_gameinfo[0] not in TEAM_BASED_GAMETYPES + NONTEAM_BASED_GAMETYPES:
            self._queue.clear()
        else:
            self.check_for_opening(2)

    def handle_game_start(self, data):
        self.check_spec_time()

        @minqlx.thread
        def t():
            if self.game.type_short == "ft":
                countdown = self.get_cvar("g_freezeRoundDelay", int)
            else:
                countdown = self.get_cvar("g_roundWarmupDelay", int)
            time.sleep(max(countdown / 1000 - 0.8, 0))
            self.even_the_teams()
        t()

    def handle_map(self, mapname, factory):
        self._ignore = False
        self._ignore_msg_already_said = False
        self.end_screen = False
        self.q_gameinfo[0] = self.game.type_short
        self.check_spec_time()

    def handle_game_end(self, data):
        self.end_screen = True
        if data["ABORTED"]:
            self.check_for_opening(2)
            return

    def handle_round_countdown(self, round_num):
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
        self.look_at_teams()

    def handle_round_start(self, number):
        self.check_for_opening(0.2)
        self.check_queue(2)
        self.check_spec(2)
        self.even_the_teams()

    def handle_round_end(self, data):
        if self.q_gameinfo[0] in NO_COUNTDOWN_TEAM_GAMES:
            self.check_for_opening(0.2)
            self.even_the_teams(True)
            if self.get_cvar("qlx_queueQueueMsg", bool):
                self.cmd_list_queue()
            if self.get_cvar("qlx_queueSpecMsg", bool):
                self.cmd_list_specs()
        self.check_spec_time()

    def death_monitor(self, victim, killer, data):
        if self.q_gameinfo[0] in NON_ROUND_BASED_GAMETYPES:
            self.death_count += 1
            if self.death_count > 5 and self.death_count > self.q_gameinfo[2] / 5:
                self.check_for_opening(0.2)
                if self.get_cvar("qlx_queueQueueMsg", bool):
                    self.cmd_list_queue()
                if self.get_cvar("qlx_queueSpecMsg", bool):
                    self.cmd_list_specs()
                self.check_queue(0.2)
                self.check_spec(0.2)
                self.death_count = 0
                self.check_spec_time()

    def handle_console_print(self, text):
        if 'now locked' in text or 'now unlocked' in text:
            if text.find('broadcast: print "The RED team is now locked') != -1:
                self.red_locked = True
            elif text.find('broadcast: print "The BLUE team is now locked') != -1:
                self.blue_locked = True
            elif text.find('broadcast: print "The RED team is now unlocked') != -1:
                self.red_locked = False
                self.check_for_opening(0.2)
            elif text.find('broadcast: print "The BLUE team is now unlocked') != -1:
                self.blue_locked = False
                self.check_for_opening(0.2)

    def handle_vote_ended(self, votes, vote, args, passed):
        if passed and vote == "teamsize":
            self.check_for_opening(2.5)

    # ==============================================
    #               Plugin functions
    # ==============================================

    def get_max_players(self):
        max_players = self.get_cvar("teamsize", int)
        if self.q_gameinfo[0] in TEAM_BASED_GAMETYPES:
            max_players *= 2
        if max_players == 0:
            max_players = self.get_cvar("sv_maxClients", int)
        return max_players

    def add_to_queue_pos(self, player, pos):
        self.remove_from_queue(player)
        self.remove_from_spec(player)
        self._queue.add_to_queue_pos(player.steam_id, player, pos)
        self.cmd_list_queue()
        self.check_for_opening(0.5)

    def add_to_queue(self, player):
        self.remove_from_spec(player)
        self._queue.add_to_queue(player.steam_id, player)
        position = self._queue.get_queue_position(player)
        player.center_print("^7You are in the ^4Queue^7 position ^1{}^7\nType ^4{}q ^7to show the queue"
                            .format(position + 1, self.get_cvar("qlx_commandPrefix")))
        self.check_for_opening(0.2)

    def remove_from_queue(self, player):
        if player in self._queue:
            self._queue.remove_from_queue(player.steam_id, player)

    def check_queue(self, delay=0.1):
        if not self.end_screen and not self.displaying_queue and self._queue.size() > 0\
                and self.get_cvar("qlx_queueQueueMsg", bool):
            self.displaying_queue = True
            self.queue_message(delay)

    @minqlx.thread
    def queue_message(self, delay):
        n = self._queue.get_queue_names()
        time.sleep(delay)
        queue_show = self.get_cvar("qlx_queueQueueMsg", int)
        count = 1
        for p in n:
            if queue_show == 2 and self._round % 5 != 0:
                continue
            try:
                p.center_print("^7You are in ^4Queue ^7position ^1{}".format(count))
            except:
                pass
            count += 1
        self.displaying_queue = False

    def add_spectators(self):
        for player in self.teams()["spectator"]:
            self.add_to_spec(player)

    def add_to_spec(self, player):
        self._spec.add_to_spec(player.steam_id)
        player.center_print("^6Spectate Mode\n^7Type ^4!s ^7to show spectators.")

    def remove_from_spec(self, player):
        self._spec.remove_from_spec(player.steam_id)

    def check_spec(self, delay=0.0):
        if not self.end_screen and not self.displaying_spec and self._spec.size() > 0\
                and self.get_cvar("qlx_queueSpecMsg", bool):
            self.displaying_spec = True
            self.spec_message(delay)

    @minqlx.thread
    def spec_message(self, delay=0.0):
        time.sleep(delay)
        spec_show = self.get_cvar("qlx_queueSpecMsg", int)
        spectators = self.teams()["spectator"]
        if self._spec.size() > 0 and len(spectators) > 0:
            s = self._spec.get_spectators()
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
                    if 0 < max_spec_time < 9999 and\
                            self.db.get_permission(int(p)) < self.get_cvar("qlx_queueAdmin", int):
                        spec.center_print("^6Spectate Mode for {}\n^7Join the game to ^1play ^7or enter the ^4Queue.\n"
                                          "You can remain in spectate for ^1{} ^7minutes."
                                          .format(spec_time, max_spec_time))
                    else:
                        spec.center_print("^6Spectate Mode for {}\n^7Join the game to ^1play ^7or enter the ^4Queue"
                                          .format(spec_time))
        self.displaying_spec = False

    def check_for_opening(self, delay=0.0):
        if not self.checking_space:
            self.check_for_space(delay)

    @minqlx.thread
    def check_for_space(self, delay):
        if self._queue.size() == 0 or self.end_screen:
            return

        self.checking_space = True

        if delay > 0.0:
            time.sleep(delay)

        state = self.game.state
        max_players = self.get_max_players()
        teams = self.teams()
        red_players = len(teams["red"])
        blue_players = len(teams["blue"])
        free_players = len(teams["free"])
        if self.q_gameinfo[0] in NONTEAM_BASED_GAMETYPES:
            if free_players < max_players:
                self.place_in_team(max_players - free_players, "free")
            else:
                self.checking_space = False

        elif self.q_gameinfo[0] in TEAM_BASED_GAMETYPES:
            ts = int(self.game.teamsize)
            if ts == 0:
                ts = int(max_players / 2)
            difference = red_players - blue_players
            if difference < 0 and not self.red_locked:
                self.place_in_team(abs(difference), "red")
            elif difference > 0 and not self.blue_locked:
                self.place_in_team(difference, "blue")
            elif (red_players + blue_players) < max_players:
                if self._queue.size() > 1 and not self.red_locked and not self.blue_locked:
                    self.place_in_both()
                elif state == "warmup":
                    if not self.blue_locked and blue_players < ts:
                        self.place_in_team(1, "blue")
                    elif not self.red_locked and red_players < ts:
                        self.place_in_team(1, "red")
                    else:
                        self.checking_space = False
                else:
                    self.checking_space = False
            else:
                self.checking_space = False
        else:
            self.checking_space = False

    def place_in_team(self, amount, team):
        with self.rlock:
            if not self.end_screen:
                count = 0
                teams = self.teams()
                while count < amount and self._queue.size():
                    p = self._queue.get_next()
                    if p[1] in teams["spectator"]and p[1].connection_state == "active":
                        self.team_placement(p[1], team)
                        if team in "red":
                            placement = "^1red ^7team"
                        elif team == "blue":
                            placement = "^4blue ^7team"
                        else:
                            placement = "battle"
                        self.msg("{} ^7has joined the {}.".format(p[1], placement))
                        count += 1
            self.checking_space = False
            return

    def place_in_both(self):
        with self.rlock:
            if not self.end_screen and self._queue.size() > 1:
                teams = self.teams()
                spectators = teams["spectator"]
                p1_sid = self._queue[0][0]
                p2_sid = self._queue[1][0]
                # Get red team's and blue team's score so the correct player placements can be executed
                red_score = int(self.game.red_score)
                blue_score = int(self.game.blue_score)
                score_diff = abs(red_score - blue_score) >= self.get_cvar("qlx_queueTeamScoresDiff", int)
                by_team = self.get_cvar("qlx_queuePlaceByTeamScores", bool)
                if self.q_gameinfo[0] in BDM_GAMETYPES:
                    red_bdm = self.team_average(teams["red"])
                    blue_bdm = self.team_average(teams["blue"])
                    p1_bdm = self.get_rating(p1_sid)
                    p2_bdm = self.get_rating(p2_sid)
                    # set team related variables initial values
                    # If the team's score difference is over "qlx_queuesTeamScoresAmount" and
                    #  "qlx_queuesPlaceByTeamScore" is enabled players will be placed with the higher bdm
                    #  player going to the lower scoring team regardless of average team BDMs
                    if by_team and score_diff:
                        if p1_bdm > p2_bdm:
                            placement = ["blue", "red"] if red_score > blue_score else ["red", "blue"]
                        else:
                            placement = ["red", "blue"] if red_score > blue_score else ["blue", "red"]
                    # Executes if the 'place by team score' doesn't execute and sets player
                    #   with higher BDM on the team with the lower average BDM.
                    else:
                        if red_bdm > blue_bdm:
                            placement = ["blue", "red"] if p1_bdm > p2_bdm else ["red", "blue"]
                        elif blue_bdm > red_bdm:
                            placement = ["red", "blue"] if p1_bdm > p2_bdm else ["blue", "red"]
                        else:
                            if red_score > blue_score:
                                placement = ["blue", "red"] if p1_bdm > p2_bdm else ["red", "blue"]
                            else:
                                placement = ["red", "blue"] if p1_bdm > p2_bdm else ["blue", "red"]
                    player1 = self._queue.get_next()
                    if player1[1] in spectators and player1[1].connection_state == "active":
                        player2 = self._queue.get_next()
                        if player2[1] in spectators and player2[1].connection_state == "active":
                            self.team_placement(player1[1], placement[0])
                            self.msg("{} ^7has joined the {}{} ^7team."
                                     .format(player1[1], "^1" if placement[0] == "red" else "^4", placement[0]))
                            self.team_placement(player2[1], placement[1])
                            self.msg("{} ^7has joined the {}{} ^7team."
                                     .format(player2[1], "^1" if placement[1] == "red" else "^4", placement[1]))
                        else:
                            self.add_to_queue_pos(player1[1], 0)
                else:
                    player1 = self._queue.get_next()
                    if player1[1] in spectators and player1[1].connection_state == "active":
                        player2 = self._queue.get_next()
                        if player2[1] in spectators and player2[1].connection_state == "active":
                            players = self._queue.get_two_from_queue()
                            self.team_placement(player1[1], "blue")
                            self.msg("{} ^7has joined the ^4blue ^7team.".format(players[1]))
                            self.team_placement(player2[1], "red")
                            self.msg("{} ^7has joined the ^1red ^7team.".format(players[3]))
                        else:
                            self.add_to_queue_pos(player1[1], 0)
            self.checking_space = False
            return

    def get_rating(self, sid):
        if self.get_cvar("g_factory").lower() == "ictf":
            game_type = "ictf"
        else:
            game_type = self.q_gameinfo[0]
        if self.db.exists(BDM_KEY.format(sid, game_type, "rating")):
            return int(self.db.get(BDM_KEY.format(sid, game_type, "rating")))
        else:
            return self.get_cvar("qlx_bdmDefaultBDM", int)

    def team_average(self, team):
        """Calculates the average rating of a team."""
        avg = 0
        if team:
            for p in team:
                avg += self.get_rating(p.steam_id)
            avg /= len(team)
        return int(round(avg))

    @minqlx.next_frame
    def team_placement(self, player, team):
        player.put(team)

    @minqlx.thread
    def add_join_times(self):
        players = self.players()
        for player in players:
            self._join.add_to_jt(player.steam_id)

    def add_to_join(self, player):
        self._join.add_to_jt(player.steam_id)

    def remove_from_join(self, player):
        self._join.remove_from_jt(player.steam_id)

    def get_join_time(self, player):
        if player.steam_id not in self._join:
            self.add_to_join(player)
            return time.time()
        return self._join.get_join_time(player.steam_id)

    def get_join_times(self):
        return self._join.get_jt()

    @minqlx.thread
    def look_at_teams(self):
        if self.q_gameinfo[0] in TEAM_BASED_GAMETYPES:
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

            if abs(difference) > 0 and \
                    self.get_cvar("qlx_queueMinPlayers", int) <= p_count <= self.get_cvar("qlx_queueMaxPlayers", int):
                if difference == -1:
                    self.get_player_for_spec(teams["blue"].copy())
                    spec_player = self._players[0]
                elif difference == 1:
                    self.get_player_for_spec(teams["red"].copy())
                    spec_player = self._players[0]
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
                    self.msg("^3Uneven Teams Detected^7: {} ^7will be moved to {}^7."
                             .format("^7, ".join(players), where))
                if spec_player:
                    self.msg("^3Uneven Teams Detected^7: {} ^7will be moved to ^3spectate^7.".format(spec_player))
            self.even_the_teams(True)

    @minqlx.thread
    def even_the_teams(self, delay=False):
        if self.q_gameinfo[0] not in TEAM_BASED_GAMETYPES:
            return
        if delay:
            if self.game.type_short == "ft":
                countdown = self.get_cvar("g_freezeRoundDelay", int)
            else:
                countdown = self.get_cvar("g_roundWarmupDelay", int)
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

        if abs(difference) > 0 and \
                self.get_cvar("qlx_queueMinPlayers", int) <= p_count <= self.get_cvar("qlx_queueMaxPlayers", int):
            if difference == -1:
                self.get_player_for_spec(teams["blue"].copy())
                spec_player = self._players[0]
            elif difference == 1:
                self.get_player_for_spec(teams["red"].copy())
                spec_player = self._players[0]
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
                self.msg("^3Uneven Teams Detected^7: {} ^7was moved to {}^7.".format("^7, ".join(players), where))
            if spec_player:
                self.team_placement(spec_player, "spectator")
                self.msg("^3Uneven Teams Detected^7: {} ^7was moved to ^3spectate^7.".format(spec_player))
                self.add_to_queue_pos(spec_player, 0)

    @minqlx.thread
    def get_player_for_spec(self, team):
        t_players = []
        s_players = []
        lowest_time = 0
        lowest_score = 999
        for player in team:
            if self.get_join_time(player) > lowest_time:
                lowest_time = self.get_join_time(player)
                t_players = [player]
            elif self.get_join_time(player) == lowest_time:
                t_players.append(player)
            if player.stats.score < lowest_score:
                lowest_score = player.stats.score
                s_players = [player]
            elif player.stats.score == lowest_score:
                s_players.append(player)
        if self.get_cvar("qlx_queueSpecByTime", bool) and self.get_cvar("qlx_queueSpecByScore", bool):
            if self.get_cvar("qlx_queueSpecByPrimary") == "score":
                if len(s_players) > 1:
                    self._players = [t_players[0]]
                else:
                    self._players = [s_players[0]]
            else:
                if len(t_players) > 1:
                    self._players = [s_players[0]]
                else:
                    self._players = [t_players[0]]
        elif self.get_cvar("qlx_queueSpecByScore", bool):
            if len(s_players) > 1:
                self._players = [s_players[randint(0, len(s_players) - 1)]]
            else:
                self._players = [s_players[0]]
        else:
            if len(t_players) > 1:
                self._players = [t_players[randint(0, len(t_players) - 1)]]
            else:
                self._players = [t_players[0]]
        return

    def return_spec_player(self, team):
        self.get_player_for_spec(team)
        return [self._players[0]]

    @minqlx.thread
    def get_uneven_players(self, team, amount):
        t_players = {}
        s_players = {}
        self._players = []
        for player in team:
            t_players[str(self.get_join_time(player))] = player
            s_players[str(player.stats.score)] = player

        if self.get_cvar("qlx_queueSpecByTime", bool) and self.get_cvar("qlx_queueSpecByScore", bool):
            if self.get_cvar("qlx_queueSpecByPrimary") == "score":
                sorted_players = sorted(((k, v) for k, v in s_players.items()), reverse=False)
            else:
                sorted_players = sorted(((k, v) for k, v in t_players.items()), reverse=True)
        elif self.get_cvar("qlx_queueSpecByScore", bool):
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

    @minqlx.thread
    def check_spec_time(self):
        max_spec_time = self.get_cvar("qlx_queueMaxSpecTime", int)
        if 0 < max_spec_time < 9999:
            admin = self.get_cvar("qlx_queueAdmin", int)
            spectators = self.teams()["spectator"]
            if self._spec.size() > 0 and len(spectators) > 0:
                s = self._spec.get_spectators()
                for p, t in s.items():
                    spec = self.player(int(p))
                    if spec in spectators:
                        if self.db.get_permission(int(p)) >= admin:
                            continue
                        time_in_spec = round((time.time() - t)) / 60
                        if time_in_spec >= max_spec_time:
                            spec.kick("was in spectate, not the queue, for too long.")
                    else:
                        self.remove_from_spec(spec)

    # ==============================================
    #               Minqlx Bot Commands
    # ==============================================
    def ignore_imbalance(self, player, msg, channel):
        self.msg("^3The move to ^1spectate ^3action will be ignored this round")
        self._ignore = True

    def ignore_imbalance_latch(self, player, msg, channel):
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

    def cmd_queue_add(self, player, msg, channel):
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
            self.add_to_queue(target_player)

    def cmd_qversion(self, player, msg, channel):
        channel.reply("^7This server has installed ^2{0} version {1} by BarelyMiSSeD\n"
                      "https://github.com/BarelyMiSSeD/minqlx-plugins/{0}.py"
                      .format(self.__class__.__name__, VERSION))

    @minqlx.thread
    def cmd_list_queue(self, player=None, msg=None, channel=None):
        spectators = self.teams()["spectator"]
        count = 0
        message = []
        if self._queue.size() > 0 and len(spectators) > 0:
            for n in range(0, self._queue.size()):
                spec = self._queue[n]
                if spec[1] in spectators:
                    t = self._queue.get_queue_time(spec[0])
                    time_in_queue = round((time.time() - t))
                    if time_in_queue / 60 > 1:
                        queue_time = "^7{}^4m^7:{}^4s^7".format(int(time_in_queue / 60), time_in_queue % 60)
                    else:
                        queue_time = "^7{}^4s^7".format(time_in_queue)
                    message.append("{} ^7[{}] ^7{}".format(spec[1], count + 1, queue_time))
                    count += 1
                else:
                    self.remove_from_queue(spec[1])
        if count == 0:
            message = ["^4No one is in the queue."]
        if channel:
            channel.reply("^2Queue^7: " + ", ".join(message))
        elif player or count:
            self.msg("^2Queue^7: " + ", ".join(message))

    @minqlx.thread
    def cmd_list_specs(self, player=None, msg=None, channel=None):
        spectators = self.teams()["spectator"]
        count = 0
        message = []
        if self._spec.size() > 0 and len(spectators) > 0:
            s = self._spec.get_spectators()
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
