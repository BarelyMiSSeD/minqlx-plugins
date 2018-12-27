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
set qlx_brLast2Damage "50"
// set the seconds delay between checking for last 2 player contact
set qlx_brDamageDelay "30"
// If the last 2 are still alive after this many time periods, slap for damage every time period
// Set this to a high value to disable.
set qlx_brSlapAfterTimePeriods "2"
// Added for the 'qlx_brSlapAfterTimePeriods'. If qlx_brSlapAfterTimePeriods is enabled this will half the time
//  periods between the slaps/damage. (0=off, 1=on, any number above 1 will be added by qlx_brSlapAfterTimePeriods
//  and that amount of rounds after the qlx_brSlapAfterTimePeriods starts the time between slaps will be half).
set qlx_brHalfTimePeriod "2"
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

VERSION = "1.1.2"

# Settings used in Battle Royale (These settings get executed on script initialization)
SETTINGS = ["g_teamSizeMin 3", "g_infiniteAmmo 0", "g_startingWeapons 23", "g_startingArmor 100",
            "g_startingHealth 200", "dmflags 20", "g_startingHealthBonus 200", "g_spawnItemPowerup 0", "fraglimit 50",
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

        # Minqlx bot commands
        self.add_command(("q", "queue"), self.cmd_list_queue)
        self.add_command(("s", "specs"), self.cmd_list_specs)
        self.add_command("score", self.cmd_score)
        self.add_command("rules", self.cmd_rules)
        self.add_command(("addqueue", "addq"), self.cmd_queue_add, self.get_cvar("qlx_brAdmin", int))
        self.add_command(("brversion", "brv"), self.cmd_br_version)
        self.add_command("restart", self.resart_br, self.get_cvar("qlx_brAdmin", int))
        self.add_command("gamestatus", self.game_status, 5)

        # Script Variables, Lists, and Dictionaries
        self.lock = Lock()
        self._queue = PlayerQueue()
        self._spec = Spectators()
        self._wins = {}
        self._rounds = 0
        self._deaths = 0
        self.last_2 = False
        self.last_two = []
        self._forfeit_game = False
        self._bonus = [self.get_cvar("qlx_brKillHealthBonus", int), self.get_cvar("qlx_brKillArmorBonus", int)]

        # Initialize Commands
        self.initialize_settings()

    # ==============================================
    #               Event Handler's
    # ==============================================
    def handle_player_loaded(self, player):
        player.tell("^4Welcome to ^1Quake ^7Live ^2Battle Royale^7.\nThis is a Last Standing type of game.\n"
                    "Type ^1{}rules ^7to see game rules.".format(self.get_cvar("qlx_commandPrefix")))
        player.center_print("^4Welcome to ^1Quake ^7Live ^2Battle Royale^7.\nThis is a Last Standing type of game.\n"
                            "Type ^1{}rules ^7to see game rules.".format(self.get_cvar("qlx_commandPrefix")))

    def handle_player_disconnect(self, player, reason):
        self.remove_from_spec(player)
        self.remove_from_queue(player)
        try:
            del self._wins[player.steam_id]
        except KeyError:
            pass
        except Exception as e:
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
        self._deaths = 0

    @minqlx.delay(1)
    def handle_game_countdown(self):
        del self.last_two[:]
        self.last_2 = False
        self._deaths = 0
        self.center_print("^4Win ^1{} ^4rounds ^7to win the ^4Game\n^7Type ^1{}score ^7to see current standings."
                          .format(self.get_cvar("qlx_brWinRounds", int), self.get_cvar("qlx_commandPrefix")))

    def handle_game_start(self, data):
        self._rounds += 1
        del self.last_two[:]
        self.last_2 = False
        if len(self.teams()["free"]) == 2:
            self.last_2 = True

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
        if self.game.state == "in_progress" and self._rounds > 0:
            minqlx.console_print("^2Killer {} : Victim {}".format(killer, victim))
            free = self.teams()["free"]
            if victim == killer:
                remaining = len(free)
            else:
                remaining = len(free) - 1
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
                    self.move_player(victim, "spectator", True, self._deaths)
                    self._deaths += 1

            if remaining == 2 and len(self.last_two) == 0:
                self.last_two.append(killer)
                for player in free:
                    if killer != player and victim != player:
                        self.last_two.append(player)
                self.last_2 = True
                self.last_2_standing()
            elif remaining == 1:
                self.move_player(victim, "spectator", True, self._deaths)
                if killer is not None:
                    self.msg("{} ^7killed {} ^7for the round win."
                             .format(killer, victim))
                    try:
                        self._wins[killer.steam_id] += 1
                    except KeyError:
                        self._wins[killer.steam_id] = 1
                    except Exception as e:
                        minqlx.console_print("Battle Royale Death Monitor Round Win Exception: {}".format(e))
                    self._deaths = 0
                    self.last_2 = False
                    self.round_win(killer, killer.health, killer.armor)
                else:
                    for player in free:
                        if victim.steam_id != player.steam_id:
                            winner = player
                    self.msg("{} ^4Died^7, giving {} ^7the round win. ^1{} ^7Health and ^2{} ^7Armor remaining."
                             .format(victim, winner, winner.health, winner.armor))
                    try:
                        self._wins[winner.steam_id] += 1
                    except KeyError:
                        self._wins[winner.steam_id] = 1
                    except Exception as e:
                        minqlx.console_print("Battle Royale Death Monitor Round Win Exception: {}".format(e))
                    self._deaths = 0
                    self.last_2 = False
                    self.round_win(winner, winner.health, winner.armor)

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
        player.tell("^1Quake ^7Live ^4Battle Royale^7:\nA round based game based in the Free For All game type. "
                    "Win ^1{} ^7rounds to win the Match. If you die in a round you have to spectate until the start of"
                    " the next round. Be the last one alive and you win a round. The last 2 standing are subject to"
                    " server enforced damage if the round lasts too long. It is possible to be killed by the server"
                    " if your health is too low."
                    .format(self.get_cvar("qlx_brWinRounds", int)))

    def cmd_score(self, player=None, msg=None, channel=None):
        self.show_score()

    @minqlx.thread
    def show_score(self):
        if len(self._wins) > 0:
            message = ["^3Current Round Win Standings^7: (^6{} ^7round wins needed to win the match)"
                       .format(self.get_cvar("qlx_brWinRounds", int))]
            for sid in self._wins:
                message.append("  ^4{} ^7: {}".format(self._wins[sid], self.player(sid)))
            self.msg("\n".join(message))
        else:
            self.msg("^3No players have won a round.")

    # ==============================================
    #               Plugin Helper functions
    # ==============================================
    @minqlx.delay(2)
    def initialize_settings(self):
        for setting in SETTINGS:
            minqlx.console_command("set {}".format(setting))
        minqlx.console_command("map {} ffa".format(self.get_cvar("qlx_brLoadMap")))

    def get_max_players(self):
        max_players = self.get_cvar("teamsize", int)
        if max_players == 0:
            max_players = self.get_cvar("sv_maxClients", int)
        return max_players

    def add_to_queue_pos(self, player, pos):
        self.remove_from_queue(player)
        self.remove_from_spec(player)
        self._queue.add_to_queue_pos(player.steam_id, player, pos)

    def add_to_queue(self, player):
        self.remove_from_spec(player)
        self._queue.add_to_queue(player.steam_id, player)

    def remove_from_queue(self, player):
        if player in self._queue:
            self._queue.remove_from_queue(player.steam_id, player)

    def add_spectators(self):
        for player in self.teams()["spectator"]:
            self.add_to_spec(player)

    def add_to_spec(self, player):
        self._spec.add_to_spec(player.steam_id)
        if self.get_cvar("qlx_brTellWhenInSpecOnly", bool):
            player.center_print("^6Spectate Mode\n^7Type ^4!s ^7to show spectators.")

    def remove_from_spec(self, player):
        self._spec.remove_from_spec(player.steam_id)

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
            minqlx.console_print("LastStanding Place in Team Exception: {}".format(e))
        return

    @minqlx.next_frame
    def move_player(self, player, team, add_queue=False, queue_pos=0):
        player.put(team)
        if add_queue:
            self.add_to_queue_pos(player, queue_pos)

    @minqlx.thread
    def last_2_standing(self):
        deal_damage = self.get_cvar("qlx_brLast2Damage", int)
        delay = self.get_cvar("qlx_brDamageDelay", int)
        self.msg("^3Last 2 remaining^7. ^1{0} ^3damage every ^2{1} ^3seconds to unengaged "
                 "players begins in ^2{1} ^3seconds^7.".format(deal_damage, delay))
        damage = [self.last_two[0].stats.damage_dealt, self.last_two[1].stats.damage_dealt]
        time.sleep(delay)
        count = 1
        must_slap = self.get_cvar("qlx_brSlapAfterTimePeriods", int)
        half_time = self.get_cvar("qlx_brHalfTimePeriod", int)
        slap = self.get_cvar("qlx_brUseSlapDmg", bool)
        while self.last_2 and len(self.last_two) == 2:
            new_damage = [self.last_two[0].stats.damage_dealt, self.last_two[1].stats.damage_dealt]
            if count >= must_slap or damage == new_damage:
                for player in self.last_two:
                    health = player.health
                    armor = player.armor
                    sub_armor = int(deal_damage * .666)
                    sub_health = deal_damage - sub_armor
                    if armor <= sub_armor:
                        minqlx.set_armor(player.id, 0)
                        sub_health += sub_armor - armor
                    else:
                        minqlx.set_armor(player.id, armor - sub_armor)
                    if slap:
                        if health - sub_health <= 0:
                            minqlx.console_command("slap {} {}".format(player.id, health - 1))
                        else:
                            minqlx.console_command("slap {} {}".format(player.id, sub_health))
                    else:
                        if health - sub_health <= 0:
                            minqlx.set_health(player.id, 1)
                        else:
                            minqlx.set_health(player.id, health - sub_health)
                        player.center_print("^1Damage")
                        self.msg("{} was damaged!".foramt(player.name))
                        super().play_sound("sound/player/doom/pain75_1.wav", player)
            else:
                damage = new_damage
            if half_time > 0 and count >= must_slap + half_time:
                time.sleep(delay / 2)
            else:
                time.sleep(delay)
            count += 1

    @minqlx.delay(0.2)
    def round_win(self, player, health, armor):
        del self.last_two[:]
        if self._wins[player.steam_id] == self.get_cvar("qlx_brWinRounds", int):
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

    @minqlx.thread
    def return_players_to_game(self):
        time.sleep(0.5)
        self.place_in_team(0)
        if self._rounds > 0:
            self.allready()

    @minqlx.delay(2.5)
    def win_message(self, player, wins, rounds, win_type, health, armor):
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
            self.msg("\n".join(message))
            for p in self.teams()["free"]:
                if p.steam_id == player.steam_id:
                    super().play_sound("sound/vo/you_win.wav", p)
                else:
                    super().play_sound("sound/vo/you_lose.wav", p)
            self._wins.clear()
        else:
            self.msg("{} ^7Wins the round with ^1{} ^7Health and ^2{} ^7Armor remaining^1!!!\n"
                     "^2{} ^7current round wins, needs ^1{} ^7more"
                     .format(player, health, armor, wins, self.get_cvar("qlx_brWinRounds", int) - wins))
            self.center_print("{} ^7Wins the round^1!!!\n^2{} ^7current round wins, needs ^1{} ^7more"
                              .format(player, wins, self.get_cvar("qlx_brWinRounds", int) - wins))
            self.cmd_score()

    def game_status(self, player=None, msg=None, channel=None):
        minqlx.console_print("^6Battle Royale Game Status: ^4Map ^1- ^7{}".format(self.get_cvar("mapname")))
        teams = self.teams()
        if len(teams["free"] + teams["spectator"]) == 0:
            minqlx.console_print("^3No players connected")
        else:
            if self.game.state not in ["in_progress", "countdown"]:
                minqlx.console_print("^3Match is not in progress")
            for player in teams["free"]:
                try:
                    score = self._wins[player.steam_id]
                except KeyError:
                    score = 0
                except Exception as e:
                    score = 0
                    minqlx.console_print("Battle Royale Game Status score error: {}".format(e))
                minqlx.console_print("{}^7: ^6Round Wins ^4{} ^6Ping^7: {}".format(player, score, player.stats.ping))
            for player in teams["spectator"]:
                minqlx.console_print("^6Spectator^7: {} {}".format(player.id, player))
