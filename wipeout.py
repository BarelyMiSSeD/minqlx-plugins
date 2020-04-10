# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should review a copy of the GNU General Public License
# along with minqlx. See <http://www.gnu.org/licenses/>.

# This is a plugin for the minqlx admin bot.
# It makes a wipeout type game mode based on the Diabotical wipeout mode.
#
# Players can type 'what is wipeout' or '!wipeout' to get a description of the game type and key binding instructions.
# The command '!power' is used to switch between the 2 holdables given for each life.

"""
NOTE: THIS WILL ONLY RUN IN THE CA GAME TYPE MODE. IF THE SERVER IS CHANGED TO ANY OTHER GAME TYPE THE
 WIPEOUT GAME MODE WILL NOT PERFORM ANY ACTIONS TO THE GAME, BUT THE GAME CAN OCCUR.


//script cvars to be put in server configuration file (default: server.cfg). Default values shown.
// set the rounds needed to win to win the wipeout game
set qlx_wipeoutRounds "3"
// set the seconds added to the respawn timer for each team death
set qlx_wipeoutAddSeconds "5"
// set the probability percentage of getting kamakazi when power holdables are given
set qlx_wipeoutKamakazi "2"
// enable/disable new players being added to an active wipeout round
set qlx_wipeoutNewPlayers "1"
// set the sound to be played to the team hunting the last remaining player on the opposing team
set qlx_wipeoutHuntSound "sound/vo_evil/1_frag.ogg"
// Enable/Disable the echoing of players saying !power in chat. It is blocked by default because this
// chat command is frequently used by players during game play.
set qlx_wipeoutBlockPower "1"
"""

import minqlx
import time
import random
from threading import Lock

VERSION = "1.8"

# Settings used in Wipeout (These settings get executed on script initialization)
SETTINGS = ["roundtimelimit 18000", "g_startingweapons 8447", "g_startingAmmo_rg 50", "g_startingAmmo_rl 50",
            "g_startingAmmo_gl 25", "g_startingAmmo_lg 200", "g_startingAmmo_pg 200", "g_startingAmmo_sg 50",
            "g_startingAmmo_hmg 200", "g_startingAmmo_mg 200"]

ENABLE_LOG = True

if ENABLE_LOG:
    import logging
    import os
    from logging.handlers import RotatingFileHandler
    import datetime


class wipeout(minqlx.Plugin):
    def __init__(self):
        # wipeout cvars
        self.set_cvar_once("qlx_wipeoutRounds", "3")
        self.set_cvar_once("qlx_wipeoutAddSeconds", "5")
        self.set_cvar_once("qlx_wipeoutKamakazi", "2")
        self.set_cvar_once("qlx_wipeoutNewPlayers", "1")
        self.set_cvar_once("qlx_wipeoutBlockPower", "1")
        self.set_cvar_once("qlx_wipeoutHuntSound", "sound/vo_evil/1_frag.ogg")

        # Minqlx bot Hooks
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("round_countdown", self.handle_round_countdown)
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("death", self.handle_death)
        self.add_hook("map", self.handle_map)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("chat", self.handle_chat)
        self.add_hook("player_disconnect", self.handle_player_disconnect)

        # Minqlx bot commands
        self.add_command("power", self.cmd_power)
        self.add_command("wipeout", self.cmd_wipeout)

        self.red = minqlx.RedTeamChatChannel()
        self.blue = minqlx.BlueTeamChatChannel()

        self.player_hold = {}
        self.player_hold_lock = Lock()
        self.holding_med = {}
        self.holding_med_lock = Lock()
        self.med_used = []
        self.med_used_lock = Lock()
        self.power_used = []
        self.power_used_lock = Lock()
        self.conversion = {27: "teleporter", 34: "flight", 37: "kamikaze", 39: "invulnerability"}
        self.selections = [27, 34, 39]
        self.kamakazi = 0.0
        self.dead_players = {}
        self.dead_players_lock = Lock()
        self.team_timeout = []
        self.team_timeout_lock = Lock()
        self.length = len(self.selections)
        self.add_new = False
        self.add_seconds = 5
        self.countdown = False
        self.hunt_sound = None
        self.ca_gametype = self.game.type_short == "ca"
        self.went_to_spec = []
        self.went_to_spec_lock = Lock()
        self.block_power = self.get_cvar("qlx_wipeoutBlockPower", bool)

        if ENABLE_LOG:
            self.wipeout_log = logging.Logger(__name__)
            file_dir = os.path.join(minqlx.get_cvar("fs_homepath"), "logs")
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)

            file_path = os.path.join(file_dir, "wipeout.log")
            file_fmt = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
            file_handler = RotatingFileHandler(file_path, encoding="utf-8", maxBytes=3000000, backupCount=5)
            file_handler.setFormatter(file_fmt)
            self.wipeout_log.addHandler(file_handler)
            self.wipeout_log.info("============================= Logger started @ {} ============================="
                                  .format(datetime.datetime.now()))

    def handle_new_game(self):
        if ENABLE_LOG:
            self.wipeout_log.info("Game Starting: {}".format(datetime.datetime.now()))
        self.reset_all()
        if self.ca_gametype:
            for setting in SETTINGS:
                if ENABLE_LOG:
                    self.wipeout_log.info("Sending: {}".format(setting))
                minqlx.console_command(setting)
            if ENABLE_LOG:
                self.wipeout_log.info("Set roundlimit to {}".format(self.get_cvar("qlx_wipeoutRounds", int)))
            minqlx.console_command("roundlimit {}".format(self.get_cvar("qlx_wipeoutRounds", int)))
            self.start_timer()

    def handle_game_end(self, data):
        if ENABLE_LOG:
            self.wipeout_log.info("Game End: {}".format(datetime.datetime.now()))
        self.countdown = False
        self.reset_all()

    def handle_round_countdown(self, number):
        if ENABLE_LOG:
            self.wipeout_log.info("Round Countdown: {}".format(datetime.datetime.now()))
        self.countdown = True
        if self.ca_gametype:
            self.reset_all()
            self.assign_items()

    def handle_round_start(self, number):
        if ENABLE_LOG:
            self.wipeout_log.info("Round Start: {}".format(datetime.datetime.now()))
        self.countdown = False

    def handle_death(self, victim, killer, data):
        if ENABLE_LOG:
            dead = victim if victim is not None else "None"
            self.wipeout_log.info("Player Death: {} : {}".format(datetime.datetime.now(), dead))
        if self.ca_gametype and victim is not None:
            self.player_died(victim)

    def handle_map(self, mapname, factory):
        if ENABLE_LOG:
            self.wipeout_log.info("Map Changed: {} To: {} {}".format(datetime.datetime.now(), mapname, factory))
        self.kamakazi = self.get_cvar("qlx_wipeoutKamakazi", int) / 100.0
        self.add_new = self.get_cvar("qlx_wipeoutNewPlayers", bool)
        self.add_seconds = self.get_cvar("qlx_wipeoutAddSeconds", int)
        self.hunt_sound = self.get_cvar("qlx_wipeoutHuntSound")
        self.block_power = self.get_cvar("qlx_wipeoutBlockPower", bool)
        self.ca_gametype = self.game.type_short == "ca"
        self.countdown = False
        self.reset_all()

    def handle_team_switch(self, player, old_team, new_team):
        if ENABLE_LOG:
            self.wipeout_log.info("Team Switch: {} : {} {}".format(datetime.datetime.now(), player, new_team))
        if self.ca_gametype:
            self.process_team_switch(player, new_team)

    def handle_chat(self, player, msg, channel):
        if "what is wipeout" in msg.lower():
            self.print_instructions(player)

    def handle_player_disconnect(self, player, reason):
        if ENABLE_LOG:
            self.wipeout_log.info("Player Disconnected: {} : {}".format(datetime.datetime.now(), player))
        pid = player.id
        sid = player.steam_id
        try:
            player.update()
        except minqlx.NonexistentPlayerError:
            pass
        try:
            with self.dead_players_lock:
                if pid in self.dead_players:
                    del self.dead_players[pid]
            with self.med_used_lock:
                if pid in self.med_used:
                    self.med_used.remove(pid)
            with self.power_used_lock:
                if pid in self.power_used:
                    self.power_used.remove(pid)
            with self.went_to_spec_lock:
                if sid in self.went_to_spec:
                    self.went_to_spec.remove(sid)
        except Exception as e:
            if ENABLE_LOG:
                self.wipeout_log.info("Player Disconnected Exception: {} : {}".format(datetime.datetime.now(), [e]))

    def cmd_wipeout(self, player, msg, channel):
        self.print_instructions(player)

    def print_instructions(self, player):
        player.tell("^4Wipeout is a modified Clan Arena gametype with respawns played in Quake Live.\n"
                    "A team wins by having all the players on the opposing team dead at the same time.\n"
                    "When a player dies they spectate for a certain time period. "
                    "The time period starts at 5 seconds but is increased by {1} seconds"
                    " for each death on the player's team.\nThe first team to win {2} rounds wins the match.\n"
                    "When round starts you are given 2 power up holdables. Medkit and either\n"
                    "Invulnerability-Shield/Teleport/Flight/Kamikazee\nwith a {3} percent chance of getting kamakazi.\n"
                    "^1To use them you need to have 2 keys bound:\n"
                    "^61) ^1bind <key> \"+button2\" ^3This is the use bind\n"
                    "^62) ^1bind <key> \"say {0}power\" ^3Item swap (medkit and powerup) bind\n"
                    "Quotes used in the BIND commands need to be ^6double-quotes^3.\n"
                    "If the server is blocking saying {0}power in chat, it will not spam the server."
                    .format(minqlx.get_cvar("qlx_commandPrefix"), self.add_seconds,
                            self.get_cvar("qlx_wipeoutRounds"), self.get_cvar("qlx_wipeoutKamakazi")))

    def reset_all(self):
        if ENABLE_LOG:
            self.wipeout_log.info("Reset All: {}".format(datetime.datetime.now()))
        try:
            with self.team_timeout_lock:
                self.team_timeout = [5, 5]
            with self.dead_players_lock:
                self.dead_players.clear()
            with self.player_hold_lock:
                self.player_hold.clear()
            with self.holding_med_lock:
                self.holding_med.clear()
            with self.med_used_lock:
                del self.med_used[:]
            with self.power_used_lock:
                del self.power_used[:]
            with self.went_to_spec_lock:
                del self.went_to_spec[:]
        except Exception as e:
            if ENABLE_LOG:
                self.wipeout_log.info("Reset All Exception: {} : {}".format(datetime.datetime.now(), [e]))

    def process_team_switch(self, player, team):
        if ENABLE_LOG:
            self.wipeout_log.info("Process Team Switch: {}".format(datetime.datetime.now()))
        try:
            if self.game.state == "in_progress":
                if team in ['red', 'blue']:
                    if not self.countdown:
                        if self.add_new:
                            was_in_game = False
                            with self.went_to_spec_lock:
                                if player.steam_id in self.went_to_spec:
                                    was_in_game = True
                                    self.went_to_spec.remove(player.steam_id)
                            if was_in_game:
                                team_slot = 0 if team == "red" else 1
                                with self.team_timeout_lock:
                                    timeout = self.team_timeout[team_slot]
                                    self.team_timeout[team_slot] += self.add_seconds
                                with self.dead_players_lock:
                                    self.dead_players[player.id] = time.time() + timeout
                            else:
                                minqlx.player_spawn(player.id)
                                self.give_power_up(player)
                else:
                    with self.went_to_spec_lock:
                        if player.steam_id not in self.went_to_spec:
                            self.went_to_spec.append(player.steam_id)
                    with self.dead_players_lock:
                        if player.id in self.dead_players:
                            del self.dead_players[player.id]
        except Exception as e:
            if ENABLE_LOG:
                self.wipeout_log.info("Process Team Switch Exception: {} : {}".format(datetime.datetime.now(), [e]))

    @minqlx.delay(9.8)
    def assign_items(self):
        if ENABLE_LOG:
            self.wipeout_log.info("Assign items: {}".format(datetime.datetime.now()))
        try:
            if self.game.state in ["in_progress", "countdown"]:
                with self.player_hold_lock:
                    self.player_hold.clear()
                with self.holding_med_lock:
                    self.holding_med.clear()
                with self.med_used_lock:
                    del self.med_used[:]
                with self.power_used_lock:
                    del self.power_used[:]
                teams = self.teams()
                for player in teams["red"] + teams["blue"]:
                    self.give_power_up(player)
        except Exception as e:
            if ENABLE_LOG:
                self.wipeout_log.info("Assign items Exception: {} : {}".format(datetime.datetime.now(), [e]))

    @minqlx.next_frame
    def give_power_up(self, player):
        if ENABLE_LOG:
            self.wipeout_log.info("Give Power Up: {} : {}".format(datetime.datetime.now(), player))
        rand = random.random()
        try:
            if rand < self.kamakazi:
                select = 37
            else:
                select = self.selections[random.randrange(self.length)]
            with self.med_used_lock:
                if player.id in self.med_used:
                    self.med_used.remove(player.id)
            with self.power_used_lock:
                if player.id in self.power_used:
                    self.power_used.remove(player.id)
            minqlx.set_holdable(player.id, select)
            with self.player_hold_lock:
                self.player_hold[player.id] = select
            with self.holding_med_lock:
                self.holding_med[player.id] = False
            if select == 34:
                player.flight(fuel=10000, max_fuel=10000, thrust=2500, refuel=0)
        except Exception as e:
            if ENABLE_LOG:
                self.wipeout_log.info("Give Power Up Exception: {} : {}".format(datetime.datetime.now(), [e]))

    def cmd_power(self, player, msg, channel):
        if len(msg) == 1:
            if self.game.state == "in_progress" and player.is_alive and not self.countdown:
                self.execute_power(player)
            if self.block_power:
                return minqlx.RET_STOP_ALL

    @minqlx.next_frame
    def execute_power(self, player):
        if ENABLE_LOG:
            self.wipeout_log.info("Executing Power Command: {} : {}".format(datetime.datetime.now(), player))
        try:
            held = player.state.holdable
            with self.holding_med_lock:
                holding_med = self.holding_med[player.id]
                self.holding_med[player.id] = False if holding_med else True
            if holding_med:
                if held is None:
                    with self.med_used_lock:
                        self.med_used.append(player.id)
                with self.player_hold_lock:
                    held_power = self.player_hold[player.id]
                with self.power_used_lock:
                    if player.id not in self.power_used:
                        minqlx.set_holdable(player.id, 0)
                        minqlx.set_holdable(player.id, held_power)
            else:
                if held is None:
                    with self.power_used_lock:
                        self.power_used.append(player.id)
                with self.med_used_lock:
                    if player.id not in self.med_used:
                        minqlx.set_holdable(player.id, 0)
                        minqlx.set_holdable(player.id, 28)
        except Exception as e:
            if ENABLE_LOG:
                self.wipeout_log.info("Executing Power Command Exception: {} : {}".format(datetime.datetime.now(), [e]))

    def player_died(self, player):
        if ENABLE_LOG:
            self.wipeout_log.info("Player Died: {} : {}".format(datetime.datetime.now(), player))
        try:
            if self.game.state == "in_progress" and not self.countdown:
                team = player.team
                death_time = time.time()
                team_slot = 0 if team == "red" else 1
                with self.team_timeout_lock:
                    timeout = self.team_timeout[team_slot]
                    self.team_timeout[team_slot] += self.add_seconds
                with self.dead_players_lock:
                    self.dead_players[player.id] = death_time + timeout
                if not self.countdown:
                    self.check_for_last(team)
        except Exception as e:
            if ENABLE_LOG:
                self.wipeout_log.info("Player Died Exception: {} : {}".format(datetime.datetime.now(), [e]))

    @minqlx.thread
    def check_for_last(self, team):
        if ENABLE_LOG:
            self.wipeout_log.info("Check for Last: {}".format(datetime.datetime.now()))
        try:
            teams = self.teams()
            count = self.team_count(teams[team])
            if count == 1:
                if team == "red":
                    for p in teams["blue"]:
                        super().play_sound(self.hunt_sound, p)
                else:
                    for p in teams["red"]:
                        super().play_sound(self.hunt_sound, p)
        except Exception as e:
            if ENABLE_LOG:
                self.wipeout_log.info("Check for Last Exception: {} : {}".format(datetime.datetime.now(), [e]))

    def team_count(self, team):
        try:
            count = 0
            for player in team:
                try:
                    player.update()
                    if player.is_alive:
                        count += 1
                except minqlx.NonexistentPlayerError:
                    continue
            return count
        except Exception as e:
            if ENABLE_LOG:
                self.wipeout_log.info("Team Count Exception: {} : {}".format(datetime.datetime.now(), [e]))

    @minqlx.thread
    def start_timer(self):
        if ENABLE_LOG:
            self.wipeout_log.info("Respawn Timer Process Starting: {}".format(datetime.datetime.now()))
        count = 0
        current = time.time()
        while self.game.state in ["in_progress", "countdown"]:
            try:
                keys = []
                with self.dead_players_lock:
                    for key, value in self.dead_players.items():
                        if value <= current:
                            minqlx.player_spawn(key)
                            self.give_power_up(self.player(key))
                            keys.append(key)
                    for key in keys:
                        del self.dead_players[key]
                time.sleep(0.01)
                current = time.time()
                count += 1
                if count >= 100:
                    count = 0
                    lowest = [9999, 9999]
                    teams = self.teams()
                    t_count = [self.team_count(teams["red"]), self.team_count(teams["blue"])]
                    with self.dead_players_lock:
                        for key, value in self.dead_players.items():
                            spawn = int(value - current)
                            player = self.player(key)
                            player.center_print("^4Respawn in ^1{} ^4seconds".format(spawn))
                            team = player.team
                            slot = 0 if team == "red" else 1
                            if t_count[slot] == 1:
                                if spawn < lowest[slot]:
                                    lowest[slot] = spawn
                    if lowest[0] < 9999:
                        self.red.reply("^2Team Spawn in ^1{} ^2seconds".format(lowest[0]))
                    if lowest[1] < 9999:
                        self.blue.reply("^2Team Spawn in ^1{} ^2seconds".format(lowest[1]))
            except Exception as e:
                if ENABLE_LOG:
                    self.wipeout_log.info("Respawn Timer Process Exception: {} : {}"
                                          .format(datetime.datetime.now(), [e]))
