# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# This is a queueing plugin for the minqlx admin bot.
# This plugin requires the server to be using the serverBDM.py plugin

# This plugin is intended to help keep the game as enjoyable as possible, without
# the hassles of people making teams uneven, or someone joining later than others,
# but happening to hit the join button first and cutting in line when a play spot opens.
#
# The plugin will also attempt to keep team games even, when adding 2 players at once,
# by putting players into the most appropriate team, base on team scores or player BDMs.

"""
//set the minqlx permission level needed to admin this script
set qlx_queueAdmin", "3"
//The script will try to place players in by BDM ranking, if this is set on (0=off 1=on) it will
// put the higher BDM player in the losing team if the score is greater than the qlx_queueTeamScoresDiff setting
set qlx_queuePlaceByTeamScores "1"
//Set the score difference used if qlx_queuePlaceByTeamScores is on
set qlx_queueTeamScoresDiff "3"
//Display the Queue message at the start of each round
set qlx_queueQueueMsg "1"
//Display the Spectate message at the start of each round
set qlx_queueSpecMsg "1"


"""

import minqlx
import time
from threading import Lock

VERSION = "2.02.16"
TEAM_BASED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "ad", "1f", "har")
NONTEAM_BASED_GAMETYPES = ("ffa", "race", "rr")
BDM_GAMETYPES = ("ft", "ca", "ctf", "ffa", "ictf", "tdm")
NON_ROUND_BASED_GAMETYPES = ("ffa", "race", "tdm", "ctf", "har", "dom", "rr")
BDM_KEY = "minqlx:players:{}:bdm:{}:{}"


class Spectators:
    def __init__(self):
        self.spectators = {}
        self.count = 0
        self.lock = Lock()

    def __contains__(self, player):
        return player in self.spectators

    def add_to_spec(self, player):
        with self.lock:
            if player not in self.spectators:
                self.spectators[player] = time.time()
                self.count += 1

    def remove_from_spec(self, player):
        if self.count > 0:
            with self.lock:
                if player in self.spectators:
                    del self.spectators[player]
                    self.count -= 1

    def size(self):
        return self.count

    def get_spectators(self):
        with self.lock:
            return self.spectators.copy()


class PlayerQueue:
    def __init__(self):
        self.queue = []
        self.queue_player = []
        self.queue_time = {}
        self.count = 0
        self.lock = Lock()

    def __contains__(self, player):
        return player in self.queue or player in self.queue_player

    def __getitem__(self, index):
        return [self.queue[index], self.queue_player[index]]

    def add_to_queue(self, sid, player, pos=None):
        with self.lock:
            added = 0
            if sid not in self.queue:
                if pos:
                    self.queue.insert(pos, sid)
                    self.queue_player.insert(pos, player)
                    added = 2
                else:
                    self.queue.append(sid)
                    self.queue_player.append(player)
                    added = 1
                self.count += 1
                self.queue_time[str(sid)] = time.time()
            return added

    def next(self):
        return [self.queue[0], self.queue_player[0]]

    def get_next(self):
        return self.get_from_queue()

    def get_from_queue(self, pos=None):
        if self.count > 0:
            with self.lock:
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
            with self.lock:
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
            with self.lock:
                if sid in self.queue:
                    self.count -= 1
                    self.queue.remove(sid)
                    self.queue_player.remove(player)
                    del self.queue_time[str(sid)]

    def get_queue_time(self, sid):
        if str(sid) in self.queue_time:
            return self.queue_time[str(sid)]

    def get_queue_position(self, player):
        if player in self.queue:
            return self.queue.index(player)
        if player in self.queue_player:
            return self.queue_player.index(player)
        else:
            return -1

    def get_queue(self):
        with self.lock:
            return self.queue.copy()

    def get_queue_names(self):
        with self.lock:
            return self.queue_player.copy()

    def size(self):
        return self.count

    def clear(self):
        self.queue = []
        self.queue_player = []
        self.queue_time = {}
        self.count = 0


class queue(minqlx.Plugin):
    def __init__(self):
        # queue cvars
        self.set_cvar_once("qlx_queueAdmin", "3")
        self.set_cvar_once("qlx_queuePlaceByTeamScores", "1")
        self.set_cvar_once("qlx_queueTeamScoresDiff", "3")
        self.set_cvar_once("qlx_queueQueueMsg", "1")
        self.set_cvar_once("qlx_queueSpecMsg", "1")

        # Minqlx bot Hooks
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("round_countdown", self.handle_round_countdown)
        self.add_hook("round_start", self.handle_round_start)
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

        # Script Variables, Lists, and Dictionaries
        self.lock = Lock()
        self._queue = PlayerQueue()
        self._spec = Spectators()
        self.red_locked = False
        self.blue_locked = False
        self.end_screen = False
        self.displaying_queue = False
        self.displaying_spec = False
        self.in_countdown = False
        self.death_count = 0
        self.q_gametype = self.game.type_short
        self.q_teamsize = self.get_cvar("teamsize", int)
        self.checking_space = False

        # Initialize Commands
        self.add_spectators()

    # ==============================================
    #               Event Handler's
    # ==============================================

    def handle_player_disconnect(self, player, reason):
        self.remove_from_spec(player)
        self.remove_from_queue(player)
        self.check_for_opening(0.5)

    @minqlx.next_frame
    def handle_team_switch(self, player, old_team, new_team):
        if new_team != "spectator":
            self.remove_from_spec(player)
            self.remove_from_queue(player)
        else:
            if not self.end_screen:
                self.check_for_opening(0.2)

            @minqlx.delay(1)
            def check_spectator():
                if player.steam_id not in self._queue:
                    self.add_to_spec(player)

            check_spectator()

    def handle_team_switch_attempt(self, player, old_team, new_team):
        if new_team != "spectator" and old_team == "spectator":
            if self.q_gametype in TEAM_BASED_GAMETYPES:
                teams = self.teams()
                if len(teams["red"]) + len(teams["blue"]) >= self.get_max_players()\
                        or self.game.state in ["in_progress", "countdown"] or\
                        self._queue.size() > 0 or self.red_locked or self.blue_locked:
                    self.add_to_queue(player)
                    self.remove_from_spec(player)
                    self.check_for_opening(0.2)
                    return minqlx.RET_STOP_ALL
            elif self.q_gametype in NONTEAM_BASED_GAMETYPES:
                if len(self.teams()["free"]) >= self.get_max_players()\
                        or self.game.state in ["in_progress", "countdown"] or self._queue.size() > 0:
                    self.add_to_queue(player)
                    self.remove_from_spec(player)
                    self.check_for_opening(0.2)
                    return minqlx.RET_STOP_ALL

    @minqlx.next_frame
    def handle_set_configstring(self, index, values):
        args = values.split("\\")[1:]
        if "teamsize" in args:
            teamsize = args[args.index("teamsize") + 1]
            if self.q_teamsize != teamsize:
                self.q_teamsize = teamsize
                self.check_for_opening(1.5)

    def handle_client_command(self, player, command):
        if command == "team s" and player in self.teams()["spectator"]:
            self.add_to_spec(player)
            self.remove_from_queue(player)
            player.center_print("^6You are set to spectate only")

    def handle_new_game(self):
        self.end_screen = False
        self.red_locked = False
        self.blue_locked = False
        self.displaying_queue = False
        self.displaying_spec = False

        if self.q_gametype not in TEAM_BASED_GAMETYPES + NONTEAM_BASED_GAMETYPES:
            self._queue.clear()
        else:
            self.check_for_opening(2)

    def handle_map(self, mapname, factory):
        self.end_screen = False
        self.q_gametype = self.game.type_short

    def handle_game_end(self, data):
        self.end_screen = True

    def handle_round_countdown(self, *args, **kwargs):
        self.check_for_opening(0.2)
        if self.get_cvar("qlx_queueQueueMsg", bool):
            self.cmd_list_queue()
        if self.get_cvar("qlx_queueSpecMsg", bool):
            self.cmd_list_specs()
        self.check_queue(0.2)
        self.check_spec(0.2)

    def handle_round_start(self, *args, **kwargs):
        self.check_for_opening(0.2)
        self.check_queue(2)
        self.check_spec(2)

    def death_monitor(self, victim, killer, data):
        if self.q_gametype in NON_ROUND_BASED_GAMETYPES:
            self.death_count += 1
            if self.death_count > 5:
                self.check_for_opening(0.2)
                if self.get_cvar("qlx_queueQueueMsg", bool):
                    self.cmd_list_queue()
                if self.get_cvar("qlx_queueSpecMsg", bool):
                    self.cmd_list_specs()
                self.check_queue(0.2)
                self.check_spec(0.2)
                self.death_count = 0

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
        if self.q_gametype in TEAM_BASED_GAMETYPES:
            max_players *= 2
        if max_players == 0:
            max_players = self.get_cvar("sv_maxClients", int)
        return max_players

    def add_to_queue_pos(self, player, pos):
        self.remove_from_queue(player)
        self.remove_from_spec(player)
        self._queue.add_to_queue(player.steam_id, player, pos)
        self.check_for_opening(0.5)

    def add_to_queue(self, player):
        self.remove_from_spec(player)
        self._queue.add_to_queue(player.steam_id, player)
        position = self._queue.get_queue_position(player)
        player.center_print("^7You are in the ^4Queue^7 position ^1{}^7\nType ^4{}q ^7to show the queue"
                            .format(position + 1, self.get_cvar("qlx_commandPrefix")))
        self.check_for_opening(0.2)

    def remove_from_queue(self, player):
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
        count = 1
        for p in n:
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
        self._spec.add_to_spec((str(player.steam_id)))
        player.center_print("^6Spectate Mode\n^7Type ^4!s ^7to show spectators.")

    def remove_from_spec(self, player):
        self._spec.remove_from_spec((str(player.steam_id)))

    def check_spec(self, delay=0.0):
        if not self.end_screen and not self.displaying_spec and self._spec.size() > 0\
                and self.get_cvar("qlx_queueSpecMsg", bool):
            self.displaying_spec = True
            self.spec_message(delay)

    @minqlx.thread
    def spec_message(self, delay=0.0):
        s = self.teams()["spectator"]
        time.sleep(delay)
        for p in s:
            if str(p.steam_id) in self._spec:
                try:
                    p.center_print("^6Spectate Mode\n^7Join the game to ^1play ^7or enter the ^4Queue")
                except:
                    continue
        self.displaying_spec = False

    @minqlx.next_frame
    def check_for_opening(self, delay=0.0):
        self.check_for_space(delay)

    @minqlx.thread
    def check_for_space(self, delay):
        if self.checking_space:
            return

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
        if self.q_gametype in NONTEAM_BASED_GAMETYPES:
            if free_players < max_players:
                self.place_in_team(max_players - free_players, "free")
            else:
                self.checking_space = False

        elif self.q_gametype in TEAM_BASED_GAMETYPES:
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
        with self.lock:
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
        with self.lock:
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
                if self.q_gametype in BDM_GAMETYPES:
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
                            # player1[1].put("blue")
                            self.team_placement(player1[1], "blue")
                            self.msg("{} ^7has joined the ^4blue ^7team.".format(players[1]))
                            # player2[1].put("red")
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
            game_type = self.q_gametype
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

    # ==============================================
    #               Minqlx Bot Commands
    # ==============================================

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
        if self._queue.size() > 0 and len(spectators) > 0:
            message = []
            for n in range(0, self._queue.size()):
                spec = self._queue[n]
                if spec[1] in spectators:
                    t = self._queue.get_queue_time(spec[0])
                    time_in_queue = round((time.time() - t))
                    if time_in_queue / 60 > 1:
                        queue_time = "^7{}^4m^7:{}^4s^7".format(int(time_in_queue / 60), time_in_queue % 60)
                    else:
                        queue_time = "^7{}^4s^7".format(time_in_queue)
                    message.append("{} ^7[{}] {}".format(spec[1], count + 1, queue_time))
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
        if self._spec.size() > 0 and len(spectators) > 0:
            message = []
            s = self._spec.get_spectators()
            for p, t in s.items():
                spec = self.player(int(p))
                if spec in spectators:
                    time_in_spec = round((time.time() - t))
                    if time_in_spec / 60 > 1:
                        spec_time = "^7{}^4m^7:{}^4s^7".format(int(time_in_spec / 60), time_in_spec % 60)
                    else:
                        spec_time = "^7{}^4s^7".format(time_in_spec)
                    message.append("{} {}".format(spec, spec_time))
                    count += 1
                else:
                    self.remove_from_spec(spec)
        if count == 0:
            message = ["^4No one is set to spectate only."]
        if channel:
            channel.reply("^4Spectators^7: " + ", ".join(message))
        elif player or count:
            self.msg("^4Spectators^7: " + ", ".join(message))
