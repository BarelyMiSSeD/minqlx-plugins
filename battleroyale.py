# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should review a copy of the GNU General Public License
# along with minqlx. See <http://www.gnu.org/licenses/>.

# This is a plugin for the minqlx admin bot.
# It makes a last man standing game style played in FFA with some default weapons.

"""
NOTE: THIS SCRIPT IS NOT COMPATIBLE WITH ANY OTHER QUEUE SCRIPT.
        IT PERFORMS QUEUEING ACTIONS TO FACILITATE A LAST MAN STANDING GAME.
"""

"""
//script cvars to be put in server configuration file (default: server.cfg). Default values shown.
// set the permission level for admins
set qlx_brAdmin "3"
// set the amount of rounds a player needs to win to win the match
set qlx_brWinRounds "3"
// set the health bonus given to a player when they kill an opponent
set qlx_brKillHealthBonus "50"
// set the armor bonus given to a player when they kill an opponent
set qlx_brKillArmorBonus "50"
// set the amount of damage a player gets when the last 2 players remain and no contact has happened
set qlx_brLast2Damage "25"
// set the seconds delay between checking for last 2 player contact
set qlx_brDamageDelay "15"
// If the last 2 are still alive after this many time periods, slap/damage every time period
// Set this to a high value to disable.
set qlx_brSlapAfterTimePeriods "2"
// Added for the 'qlx_brSlapAfterTimePeriods'. If qlx_brSlapAfterTimePeriods is enabled this will half the time
//  periods between the slaps/damage. (0=off, 1=on, any number above 1 will be added by qlx_brSlapAfterTimePeriods
//  and that amount of rounds after the qlx_brSlapAfterTimePeriods starts the time between slaps will be half).
set qlx_brHalfTimePeriod "3"
// Notify a player when they set themselves to spectate (0=off 1=on)
set qlx_brTellWhenInSpecOnly "1"
// Enable to use the slap function as the damage dealer for the last 2
// Slapping causes the player to move upward a little as if slapped from below
// Disabling this results in a small center print message and a sound to notify the player that damage was dealt
set qlx_brUseSlapDmg "0"
// The map loaded after the Battle Royale script initializes (loads) to ensure the SETTINGS are set
set qlx_brLoadMap "almostlost"
"""

import minqlx
import time
from threading import Lock

VERSION = "1.2.6"

# Settings used in Battle Royale (These settings get executed on script initialization)
SETTINGS = ["g_teamSizeMin 3", "g_infiniteAmmo 0", "g_startingWeapons 23", "g_startingArmor 100",
            "g_startingHealth 200", "dmflags 20", "g_startingHealthBonus 100", "g_spawnItemPowerup 0", "fraglimit 50",
            "teamsize 0", "g_weaponrespawn 1", "g_itemTimers 0", "g_specItemTimers 0", "timelimit 10",
            "g_startingAmmo_sg 10", "g_startingAmmo_rl 5", "g_startingAmmo_rg 5", "g_startingAmmo_pl 5",
            "g_startingAmmo_pg 50", "g_startingAmmo_ng 10", "g_startingAmmo_mg 100", "g_startingAmmo_lg 100",
            "g_startingAmmo_hmg 50", "g_startingAmmo_gl 10", "g_startingAmmo_cg 100", "g_startingAmmo_bfg 10",
            "g_ammoRespawn 10", "g_allowkill 0"]


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

    def add_to_queue(self, sid, player):
        with self.lock:
            added = 0
            if sid not in self.queue:
                self.queue.append(sid)
                self.queue_player.append(player)
                added = 1
                self.count += 1
                self.queue_time[str(sid)] = time.time()
            return added

    def add_to_queue_pos(self, sid, player, pos):
        with self.lock:
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


class battleroyale(minqlx.Plugin):
    def __init__(self):
        # battleroyal cvars
        self.set_cvar_once("qlx_brAdmin", "3")
        self.set_cvar_once("qlx_brWinRounds", "3")
        self.set_cvar_once("qlx_brLast2Damage", "50")
        self.set_cvar_once("qlx_brDamageDelay", "30")
        self.set_cvar_once("qlx_brKillHealthBonus", "50")
        self.set_cvar_once("qlx_brKillArmorBonus", "50")
        self.set_cvar_once("qlx_brTellWhenInSpecOnly", "1")
        self.set_cvar_once("qlx_brSlapAfterTimePeriods", "2")
        self.set_cvar_once("qlx_brHalfTimePeriod", "2")
        self.set_cvar_once("qlx_brUseSlapDmg", "0")
        self.set_cvar_once("qlx_brLoadMap", "almostlost")
        self.set_cvar_once("qlx_brLogErrors", "1")

        # Minqlx bot Hooks
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("game_countdown", self.handle_game_countdown)
        self.add_hook("game_start", self.handle_game_start)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("death", self.death_monitor)
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("team_switch_attempt", self.handle_team_switch_attempt)
        self.add_hook("set_configstring", self.handle_set_config_string)
        self.add_hook("client_command", self.handle_client_command)
        self.add_hook("vote_ended", self.handle_vote_ended)
        self.add_hook("map", self.handle_map)
        self.add_hook("server_command", self.team_placement)

        # Minqlx bot commands
        self.add_command(("q", "queue"), self.cmd_list_queue)
        self.add_command(("s", "specs"), self.cmd_list_specs)
        self.add_command("score", self.cmd_score)
        self.add_command("rules", self.cmd_rules)
        self.add_command("last2", self.last2_explanation)
        self.add_command(("addqueue", "addq"), self.cmd_queue_add, self.get_cvar("qlx_brAdmin", int))
        self.add_command(("brversion", "brv"), self.cmd_br_version)
        self.add_command("restart", self.resart_br, self.get_cvar("qlx_brAdmin", int))
        self.add_command("gamestatus", self.game_status, self.get_cvar("qlx_brAdmin", int))

        # Script Variables, Lists, and Dictionaries
        self.lock = Lock()
        self._queue = PlayerQueue()
        self._spec = Spectators()
        self._wins = {}
        self._rounds = 0
        self._deaths = 0
        self.wins_needed = self.get_cvar("qlx_brWinRounds", int)
        self.last_2 = False
        self.in_game = []
        self.last_two = []
        self._forfeit_game = False
        self._bonus = [self.get_cvar("qlx_brKillHealthBonus", int), self.get_cvar("qlx_brKillArmorBonus", int)]
        self.logging_enabled = False
        self.server_move = False

        # Initialize Commands
        self.initialize_settings()

    # ==============================================
    #               Event Handler's
    # ==============================================
    def handle_player_loaded(self, player):
        try:
            player.tell("^4Welcome to ^1Quake ^7Live ^2Battle Royale^7.\nThis is a Last Standing type of game.\n"
                        "Type ^1{}rules ^7to see game rules.".format(self.get_cvar("qlx_commandPrefix")))
            player.center_print("^4Welcome to ^1Quake ^7Live ^2Battle Royale^7.\nThis is a Last Standing type of game."
                                "\nType ^1{}rules ^7to see game rules.".format(self.get_cvar("qlx_commandPrefix")))
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Player Loaded Error: {}".format(e))

    def handle_player_disconnect(self, player, reason):
        self.remove_from_spec(player)
        self.remove_from_queue(player)
        try:
            del self._wins[player.steam_id]
        except KeyError:
            pass
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Player Disconnect Error: {}".format(e))
        self.check_for_opening(0.5)

    def handle_team_switch(self, player, old_team, new_team):
        if new_team != "spectator":
            self.remove_from_spec(player)
            self.remove_from_queue(player)
        else:
            @minqlx.delay(1)
            def check_spectator():
                if player.steam_id not in self._queue:
                    self.add_to_spec(player)
                self.check_for_opening(0.5)

            check_spectator()

    def handle_team_switch_attempt(self, player, old_team, new_team):
        try:
            if (self._rounds > 0 and old_team == "spectator" and self.game.state == "in_progress") or\
                    len(self.teams()["free"]) >= self.get_max_players():
                self.add_to_queue(player)
                self.remove_from_spec(player)
                player.center_print("^4Welcome to ^1Quake ^7Live ^2Battle Royale^7.\n^2You are in the Queue to join."
                                    "\nYou will be put into the game at round end."
                                    "\nType ^1{}rules ^7to see game rules.".format(self.get_cvar("qlx_commandPrefix")))
                return minqlx.RET_STOP_ALL
            elif new_team == "spectator":
                self.add_to_spec(player)
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("^4Handle Teams Switch Attempt Exception: {}".format(e))

    def handle_set_config_string(self, index, values):
        args = values.split("\\")[1:]
        if "teamsize" in args:
            self.check_for_opening(1.5)

    def handle_vote_ended(self, votes, vote, args, passed):
        if passed and vote == "teamsize":
            self.check_for_opening(2.5)

    def handle_client_command(self, player, command):
        if command == "team s" and player in self.teams()["spectator"]:
            self.add_to_spec(player)
            self.remove_from_queue(player)

    def handle_new_game(self):
        self._forfeit_game = False
        del self.last_two[:]
        del self.in_game[:]
        self._deaths = 0

    @minqlx.delay(1)
    def handle_game_countdown(self):
        del self.last_two[:]
        del self.in_game[:]
        self.last_2 = False
        self._deaths = 0
        self.center_print("^4Win ^1{} ^4rounds ^7to win the ^4Game\n^7Type ^1{}score ^7to see current standings."
                          .format(self.wins_needed, self.get_cvar("qlx_commandPrefix")))

    def handle_game_start(self, data):
        self._deaths = 0
        self._rounds += 1
        del self.last_two[:]
        self.last_2 = False
        if len(self.teams()["free"]) == 2:
            self.last_2 = True

        @minqlx.delay(1)
        def get_players():
            self.in_game = self.teams()["free"].copy()
        get_players()

    def handle_map(self, mapname, factory):
        del self.last_two[:]
        self._rounds = 0
        self.check_for_opening(0.5)
        self._wins.clear()

    def handle_game_end(self, data):
        if data["EXIT_MSG"] == "Players have forfeited.":
            self._forfeit_game = True
        self._deaths = 0
        self.last_2 = False
        del self.last_two[:]

    def death_monitor(self, victim, killer, data):
        with self.lock:
            if self.game.state == "in_progress" and self._rounds > 0:
                try:
                    if victim in self.in_game:
                        self.in_game.remove(victim)
                except Exception as e:
                    if self.logging_enabled:
                        minqlx.log_exception(self)
                    minqlx.console_print("^4Battle Royale Remove Victim from self.in_game Exception: {}".format(e))
                remaining = len(self.in_game)
                try:
                    if not self.last_2:
                        if killer is not None:
                            start_health = self.get_cvar("g_startingHealth", int)
                            if self._bonus[0] > 0:
                                health = killer.health
                                if health < start_health * 2 - self._bonus[0]:
                                    minqlx.set_health(killer.id, health + self._bonus[0])
                                else:
                                    minqlx.set_health(killer.id, start_health * 2)
                            if self._bonus[1] > 0:
                                armor = killer.armor
                                if armor < start_health * 2 - self._bonus[1]:
                                    minqlx.set_armor(killer.id, armor + self._bonus[1])
                                else:
                                    minqlx.set_armor(killer.id, start_health * 2)

                        @minqlx.delay(0.2)
                        def spec_player():
                            if victim in self.teams()["free"]:
                                self.move_player(victim, "spectator", True, self._deaths)

                        spec_player()
                        self._deaths += 1
                except Exception as e:
                    if self.logging_enabled:
                        minqlx.log_exception(self)
                    minqlx.console_print("^4Battle Royale Not Last 2 Death Monitor Exception: {}".format(e))

                if remaining == 2 and len(self.last_two) == 0:
                    try:
                        self.last_two = self.in_game.copy()
                        self.last_2 = True
                        self.last_2_standing()
                    except Exception as e:
                        if self.logging_enabled:
                            minqlx.log_exception(self)
                        minqlx.console_print("^4Battle Royale 2 Remaining Death Monitor Exception: {}".format(e))
                elif remaining == 1:
                    try:
                        self.move_player(victim, "spectator", True, self._deaths)
                        if killer is not None and killer != victim:
                            self.msg("{} ^7killed {} ^7for the round win.".format(killer, victim))
                            try:
                                self._wins[killer.steam_id] += 1
                            except KeyError:
                                self._wins[killer.steam_id] = 1
                            except Exception as e:
                                if self.logging_enabled:
                                    minqlx.log_exception(self)
                                minqlx.console_print("Battle Royale Death Monitor Round Win Exception: {}".format(e))
                            self._deaths = 0
                            self.last_2 = False
                            self.round_win(killer, killer.health, killer.armor)
                        else:
                            for player in self.last_two:
                                if victim.steam_id != player.steam_id:
                                    winner = player
                            self.msg("{} ^4Died^7, giving {} ^7the round win. ^1{} ^7Health and ^2{} ^7Armor remaining."
                                     .format(victim, winner, winner.health, winner.armor))
                            try:
                                self._wins[winner.steam_id] += 1
                            except KeyError:
                                self._wins[winner.steam_id] = 1
                            except Exception as e:
                                if self.logging_enabled:
                                    minqlx.log_exception(self)
                                minqlx.console_print("Battle Royale Death Monitor Round Win Exception: {}".format(e))
                            self._deaths = 0
                            self.last_2 = False
                            self.round_win(winner, winner.health, winner.armor)
                    except Exception as e:
                        if self.logging_enabled:
                            minqlx.log_exception(self)
                        minqlx.console_print("^4Battle Royale Death Monitor Exception: {}".format(e))

    def team_placement(self, player, cmd):
        if not self.server_move and cmd.startswith('print') and self._rounds > 0 and\
                self.game.state == "in_progress" and len(self.in_game) >= 2:
            if "The server has moved you to the FREE team" in cmd:
                if not self.last_2:
                    if player not in self.in_game:
                        self.in_game.append(player)
                    self.remove_from_queue(player)
                    self.remove_from_spec(player)
                    if self.logging_enabled:
                        minqlx.console_print("^4Battle Royale: {} ^1was placed into the game using admin command"
                                             .format(player))
                else:
                    @minqlx.delay(0.5)
                    def put_to_spec():
                        self.move_player(player, "spectator")
                        self.add_to_queue(player)

                    player.center_print("^3You were added to the queue^7.\n"
                                        "You will be put in game after the round ends.")
                    minqlx.console_print("^4Battle Royale: ^1Player {} was added to the active game".format(player))
                    if self.logging_enabled:
                        minqlx.console_print("^4Battle Royale: ^1placement of {} ^1into the game using admin"
                                             " command was attempted. Last2 standing condition override."
                                             .format(player))
                    put_to_spec()
            elif "The server has moved you to the SPECTATOR team" in cmd:
                if player in self.in_game:
                    self.in_game.remove(player)
        self.server_move = False

    # ==============================================
    #       Minqlx Player Command Functions
    # ==============================================
    def cmd_queue_add(self, player, msg, channel):
        if len(msg) < 2:
            self.add_to_queue(player)
        else:
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
                if self.logging_enabled:
                    minqlx.log_exception(self)
                minqlx.console_print("Battle Royale Cmd Que Add Exception: {}".format(e))
                return
            self.add_to_queue(target_player)

    def cmd_br_version(self, player, msg, channel):
        channel.reply("^7This server has installed ^2{0} version {1} by BarelyMiSSeD\n"
                      "https://github.com/BarelyMiSSeD/minqlx-plugins/{0}.py"
                      .format(self.__class__.__name__, VERSION))

    def resart_br(self, player, msg, channel):
        self.initialize_settings()

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

    def cmd_rules(self, player, msg=None, channel=None):
        player.tell("^1Quake ^7Live ^4Battle Royale^7:\nA round based game using the Free For All game type."
                    " Win ^1{} ^7rounds to win the Match. If you die in a round you have to spectate until the start of"
                    " the next round. Be the last one alive and you win a round. Kill an opponent and get a health"
                    " and/or armor bonus, which can greatly help in the quest to be the last alive. The last 2"
                    " standing are subject to server enforced damage if the round lasts too long. It can bring you"
                    " down to 1 health and 0 armor.".format(self.wins_needed))

    def last2_explanation(self, player, msg=None, channel=None):
        damage = self.get_cvar("qlx_brLast2Damage", int)
        time_period = self.get_cvar("qlx_brDamageDelay", int)
        require_damage = self.get_cvar("qlx_brSlapAfterTimePeriods", int)
        reduce_time = self.get_cvar("qlx_brHalfTimePeriod", int)
        player.tell("^1Quake ^7Live ^4Battle Royale ^1Last 2^7:\nWhen the last 2 players are left, in an attempt to"
                    " speed up the game, the server deals ^1{0} ^7damage to players each ^4{1} ^7second time period."
                    " For the first ^3{2} ^7time periods it will only damage the players if no damage has been"
                    " dealt by another player. The server will deal the damage no matter what for next ^3{3} ^7time"
                    " periods. And after ^3{4} ^7time periods the interval between time periods will reduce to"
                    " ^3{5} ^7seconds and continue to damage the players. The server can damage a player to ^11"
                    " ^7health and ^40 ^7armor, but it will not kill a player."
                    .format(damage, time_period, require_damage, reduce_time, require_damage + reduce_time,
                            time_period / 2)
                    )

    def game_status(self, player=None, msg=None, channel=None):
        if player:
            player.tell("^6Battle Royale Game Status: ^1{} ^3Rounds Played ^4Map ^1- ^7{}"
                        .format(self._rounds, self.get_cvar("mapname")))
        else:
            minqlx.console_print("^6Battle Royale Game Status: ^1{} ^3Rounds Played ^4Map ^1- ^7{}"
                                 .format(self._rounds, self.get_cvar("mapname")))
        teams = self.teams()
        if len(teams["free"] + teams["spectator"]) == 0:
            minqlx.console_print("^3No players connected")
        else:
            if self.game.state not in ["in_progress", "countdown"]:
                if player:
                    player.tell("^3Match is not in progress")
                else:
                    minqlx.console_print("^3Match is not in progress")
            for p in teams["free"]:
                try:
                    score = self._wins[p.steam_id]
                except KeyError:
                    score = 0
                except Exception as e:
                    score = 0
                    if self.logging_enabled:
                        minqlx.log_exception(self)
                    minqlx.console_print("Battle Royale Game Status score error: {}".format(e))
                if player:
                    player.tell("{}^7: ^6Round Wins ^4{} ^6Ping^7: {}".format(p, score, p.stats.ping))
                else:
                    minqlx.console_print("{}^7: ^6Round Wins ^4{} ^6Ping^7: {}".format(p, score, p.stats.ping))
            for p in teams["spectator"]:
                if player:
                    player.tell("^6Spectator^7: {} {} ^6Ping^7: {}".format(p.id, p, p.stats.ping))
                else:
                    minqlx.console_print("^6Spectator^7: {} {} ^6Ping^7: {}".format(p.id, p, p.stats.ping))

    def cmd_score(self, player=None, msg=None, channel=None):
        self.show_score()

    # ==============================================
    #               Plugin Helper functions
    # ==============================================
    @minqlx.delay(2)
    def initialize_settings(self):
        for setting in SETTINGS:
            minqlx.console_command("set {}".format(setting))
        minqlx.console_command("map {} ffa".format(self.get_cvar("qlx_brLoadMap")))
        self.logging_enabled = self.get_cvar("qlx_brLogErrors", bool)
        if self.logging_enabled:
            self.logger.info("Initializing Battle Royale Version {}: Changing map to {}"
                             " and setting server to settings: {}"
                             .format(VERSION, self.get_cvar("qlx_brLoadMap"), SETTINGS))

    @minqlx.thread
    def show_score(self):
        if len(self._wins) > 0:
            message = ["^3Current Round Win Standings^7: (^6{} ^7round wins needed to win the match)"
                       .format(self.wins_needed)]
            for sid in self._wins:
                message.append("  ^4{} ^7: {}".format(self._wins[sid], self.player(sid)))
            self.msg("\n".join(message))
        else:
            self.msg("^3No players have won a round.")

    def get_max_players(self):
        max_players = self.get_cvar("teamsize", int)
        if max_players == 0:
            max_players = self.get_cvar("sv_maxClients", int)
        return max_players

    def add_to_queue_pos(self, player, pos):
        try:
            self.remove_from_queue(player)
            self.remove_from_spec(player)
            self._queue.add_to_queue_pos(player.steam_id, player, pos)
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Add To Queue Position error: {}".format(e))

    def add_to_queue(self, player):
        try:
            self.remove_from_spec(player)
            self._queue.add_to_queue(player.steam_id, player)
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Add to Queue error: {}".format(e))

    def remove_from_queue(self, player):
        try:
            if player in self._queue:
                self._queue.remove_from_queue(player.steam_id, player)
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Remove from Queue error: {}".format(e))

    def add_spectators(self):
        try:
            for player in self.teams()["spectator"]:
                self.add_to_spec(player)
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Add Spectators error: {}".format(e))

    def add_to_spec(self, player):
        try:
            self._spec.add_to_spec(player.steam_id)
            if self.get_cvar("qlx_brTellWhenInSpecOnly", bool):
                player.center_print("^6Spectate Mode\n^7Type ^4!s ^7to show spectators.")
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Add to Spec error: {}".format(e))

    def remove_from_spec(self, player):
        try:
            self._spec.remove_from_spec(player.steam_id)
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Remove from Spec error: {}".format(e))

    @minqlx.thread
    def check_for_opening(self, delay=0.0):
        if self._queue.size() == 0 or self._rounds > 0:
            return

        if delay > 0.0:
            time.sleep(delay)

        try:
            max_players = self.get_max_players()
            free_players = len(self.teams()["free"])
            if free_players < max_players:
                self.place_in_team(max_players - free_players)
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("LastStanding Check For Openings Exception: {}".format(e))
        return

    def place_in_team(self, amount=0):
        try:
            if amount == 0:
                amount = self.get_max_players() - len(self.teams()["free"])
            count = 0
            teams = self.teams()
            while count < amount and self._queue.size() > 0:
                p = self._queue.get_next()
                if p[1] in teams["spectator"] and p[1].connection_state == "active":
                    self.move_player(p[1], "free")
                    self.msg("{} ^7has joined the battle.".format(p[1]))
                    count += 1
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("LastStanding Place in Team Exception: {}".format(e))
        return

    @minqlx.next_frame
    def move_player(self, player, team, add_queue=False, queue_pos=0):
        try:
            location = team if team != "spectator" else "spec"
            self.server_move = True
            minqlx.console_command("put {} {}".format(player.id, location))
            if location == "spec":
                player.center_print("^3You were ^1killed^7.\nYou will be put back in game after the round ends.")
            if add_queue:
                if queue_pos == -1:
                    self.add_to_queue(player)
                else:
                    self.add_to_queue_pos(player, queue_pos)
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Move Player error: {}".format(e))

    @minqlx.thread
    def last_2_standing(self):
        deal_damage = self.get_cvar("qlx_brLast2Damage", int)
        delay = self.get_cvar("qlx_brDamageDelay", int)
        for pl in self.players():
            super().play_sound("sound/vo/sudden_death.ogg", pl)
        self.msg("^3Last 2 remaining^7. ^1{0} ^3damage every ^2{1} ^3seconds to unengaged "
                 "players begins in ^2{1} ^3seconds^7. Type {2}last2 for a complete explanation"
                 .format(deal_damage, delay, self.get_cvar("qlx_commandPrefix")))
        damage = [self.last_two[0].stats.damage_dealt, self.last_two[1].stats.damage_dealt]
        time.sleep(delay)
        count = 1
        must_slap = self.get_cvar("qlx_brSlapAfterTimePeriods", int)
        half_time = self.get_cvar("qlx_brHalfTimePeriod", int)
        slap = self.get_cvar("qlx_brUseSlapDmg", bool)
        while self.last_2 and len(self.last_two) == 2:
            try:
                new_damage = [self.last_two[0].stats.damage_dealt, self.last_two[1].stats.damage_dealt]
                if count >= must_slap or damage == new_damage:
                    specs = self.teams()["spectator"]
                    for player in self.last_two:
                        health = player.health
                        armor = player.armor
                        sub_armor = int(deal_damage * .666)
                        sub_health = deal_damage - sub_armor
                        if armor <= sub_armor:
                            set_armor = 0
                            minqlx.set_armor(player.id, 0)
                            sub_health += sub_armor - armor
                        else:
                            set_armor = armor - sub_armor
                            minqlx.set_armor(player.id, set_armor)
                        if slap:
                            if health - sub_health <= 0:
                                minqlx.console_command("slap {} {}".format(player.id, health - 1))
                                if self.logging_enabled:
                                    minqlx.console_print("{} was damaged! ^4Health ^2{} ^7to ^1{} ^7:"
                                                         " ^4Armor ^2{} ^7to ^1{}"
                                                         .format(player, health, 1, armor, set_armor))
                                for p in specs:
                                    p.tell("{} was damaged! ^4Health ^2{} ^7to ^1{} ^7: ^4Armor ^2{} ^7to ^1{}"
                                           .format(player, health, 1, armor, set_armor))
                            else:
                                minqlx.console_command("slap {} {}".format(player.id, sub_health))
                                set_health = health - sub_health
                                if self.logging_enabled:
                                    minqlx.console_print("{} was damaged! ^4Health ^2{} ^7to ^1{} ^7:"
                                                         " ^4Armor ^2{} ^7to ^1{}"
                                                         .format(player, health, set_health, armor, set_armor))
                                for p in specs:
                                    p.tell("{} was damaged! ^4Health ^2{} ^7to ^1{} ^7: ^4Armor ^2{} ^7to ^1{}"
                                           .format(player, health, set_health, armor, set_armor))
                        else:
                            if health - sub_health <= 0:
                                set_health = 1
                                minqlx.set_health(player.id, 1)
                            else:
                                set_health = health - sub_health
                                minqlx.set_health(player.id, set_health)
                            player.center_print("^1Damage")
                            super().play_sound("sound/player/doom/pain75_1.wav", player)
                            if self.logging_enabled:
                                minqlx.console_print("{} was damaged! ^4Health ^2{} ^7to ^1{} ^7:"
                                                     " ^4Armor ^2{} ^7to ^1{}"
                                                     .format(player, health, set_health, armor, set_armor))
                            for p in specs:
                                p.tell("{} was damaged! ^4Health ^2{} ^7to ^1{} ^7: ^4Armor ^2{} ^7to ^1{}"
                                       .format(player, health, set_health, armor, set_armor))
                else:
                    damage = new_damage
                if half_time > 0 and count >= must_slap + half_time:
                    time.sleep(delay / 2)
                else:
                    time.sleep(delay)
                count += 1
            except Exception as e:
                if self.logging_enabled:
                    minqlx.log_exception(self)
                minqlx.console_print("^4Last 2 Standing While loop Exception: {}".format(e))

    @minqlx.delay(0.2)
    def round_win(self, player, health, armor):
        try:
            del self.last_two[:]
            if self._wins[player.steam_id] == self.wins_needed:
                self.win_message(player, self._wins[player.steam_id], self._rounds, "match", health, armor)
                self._rounds = 0
            else:
                if not self._forfeit_game or self._queue.size() > 0:
                    self.win_message(player, self._wins[player.steam_id], self._rounds, "round", health, armor)
                    self.abort()
                    self.return_players_to_game()
                else:
                    self._forfeit_game = False
                    self._rounds = 0
                    self._wins.clear()
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Round Win error: {}".format(e))

    @minqlx.thread
    def return_players_to_game(self):
        try:
            time.sleep(0.5)
            self.place_in_team(0)
            if self._rounds > 0:
                self.allready()
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Return Players to Game error: {}".format(e))

    @minqlx.delay(2.5)
    def win_message(self, player, wins, rounds, win_type, health, armor):
        try:
            if win_type == "match":
                message = ["{} ^7Wins the match with ^1{} ^7Health and ^2{} ^7Armor remaining^1!!!\n"
                           " ^2{} ^7wins in ^3{} ^7rounds\n^6Other Round Winners:"
                           .format(player, health, armor, wins, rounds)]
                if rounds > wins:
                    pid = player.steam_id
                    for sid in self._wins:
                        if sid != pid:
                            message.append("  ^4{} ^7: {}".format(self._wins[sid], self.player(sid)))
                else:
                    message.append("^3No other players won a round")
                display = "\n".join(message)
                self.msg(display)
                if self.logging_enabled:
                    self.logger.info("^1Battle Royale Match Win: " + display)
                for p in self.teams()["free"]:
                    if p.steam_id == player.steam_id:
                        super().play_sound("sound/vo/you_win.wav", p)
                    else:
                        super().play_sound("sound/vo/you_lose.wav", p)
                self._wins.clear()
            else:
                display = "{} ^7Wins the round with ^1{} ^7Health and ^2{} ^7Armor remaining^1!!!\n" \
                          "^2{} ^7current round wins, needs ^1{} ^7more"\
                    .format(player, health, armor, wins, self.wins_needed - wins)
                self.msg(display)
                self.center_print("{} ^7Wins the round^1!!!\n^2{} ^7current round wins, needs ^1{} ^7more"
                                  .format(player, wins, self.wins_needed - wins))
                if self.logging_enabled:
                    self.logger.info("^6Battle Royale Round Win: " + display)
                self.cmd_score()
        except Exception as e:
            if self.logging_enabled:
                minqlx.log_exception(self)
            minqlx.console_print("Battle Royale Win Message error: {}".format(e))
