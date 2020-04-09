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

VERSION = "1.3"

# Settings used in Wipeout (These settings get executed on script initialization)
SETTINGS = ["roundtimelimit 18000", "g_startingweapons 8447", "g_startingAmmo_rg 50", "g_startingAmmo_rl 50",
            "g_startingAmmo_gl 25", "g_startingAmmo_lg 200", "g_startingAmmo_pg 200", "g_startingAmmo_sg 50",
            "g_startingAmmo_hmg 200", "g_startingAmmo_mg 200"]


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

        self.player_hold = {}
        self.holding_med = {}
        self.med_used = []
        self.power_used = []
        self.conversion = {27: "teleporter", 34: "flight", 37: "kamikaze", 39: "invulnerability"}
        self.selections = [27, 34, 39]
        self.kamakazi = 0.0
        self.dead_players = {}
        self.team_timeout = []
        self.length = len(self.selections)
        self.add_new = False
        self.add_seconds = 5
        self.countdown = False
        self.lock = Lock()
        self.hunt_sound = None
        self.ca_gametype = self.game.type_short == "ca"
        self.went_to_spec = []
        self.block_power = self.get_cvar("qlx_wipeoutBlockPower", bool)

    def handle_new_game(self):
        self.kamakazi = self.get_cvar("qlx_wipeoutKamakazi", int) / 100.0
        self.add_new = self.get_cvar("qlx_wipeoutNewPlayers", bool)
        self.add_seconds = self.get_cvar("qlx_wipeoutAddSeconds", int)
        self.hunt_sound = self.get_cvar("qlx_wipeoutHuntSound")
        self.block_power = self.get_cvar("qlx_wipeoutBlockPower", bool)
        with self.lock:
            self.dead_players.clear()
        self.player_hold.clear()
        self.holding_med.clear()
        del self.med_used[:]
        del self.power_used[:]
        self.team_timeout = [5, 5]
        if self.ca_gametype:
            for setting in SETTINGS:
                minqlx.console_command(setting)
            minqlx.console_command("roundlimit {}".format(self.get_cvar("qlx_wipeoutRounds", int)))
            self.start_timer()

    def handle_game_end(self, data):
        self.countdown = False
        self.reset_all()

    def handle_round_countdown(self, number):
        if self.ca_gametype:
            self.countdown = True
            self.reset_all()
            self.assign_items()

    def handle_round_start(self, number):
        if self.ca_gametype:
            self.countdown = False

    def handle_death(self, victim, killer, data):
        if self.ca_gametype and victim is not None:
            self.player_died(victim)

    def handle_map(self, mapname, factory):
        self.ca_gametype = self.game.type_short == "ca"
        self.countdown = False
        self.reset_all()

    def handle_team_switch(self, player, old_team, new_team):
        if self.ca_gametype:
            self.process_team_switch(player, new_team)

    def handle_chat(self, player, msg, channel):
        if "what is wipeout" in msg.lower():
            self.print_instructions(player)

    def handle_player_disconnect(self, player, reason):
        pid = player.id
        sid = player.steam_id
        try:
            player.update()
        except minqlx.NonexistentPlayerError:
            pass
        with self.lock:
            if pid in self.dead_players:
                del self.dead_players[pid]
        if pid in self.med_used:
            self.med_used.remove(pid)
        if pid in self.power_used:
            self.power_used.remove(pid)
        if sid in self.went_to_spec:
            self.went_to_spec.remove(sid)

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
        self.kamakazi = self.get_cvar("qlx_wipeoutKamakazi", int) / 100.0
        self.add_new = self.get_cvar("qlx_wipeoutNewPlayers", bool)
        self.add_seconds = self.get_cvar("qlx_wipeoutAddSeconds", int)
        self.hunt_sound = self.get_cvar("qlx_wipeoutHuntSound")
        self.block_power = self.get_cvar("qlx_wipeoutNewPlayers", bool)
        self.team_timeout = [5, 5]
        with self.lock:
            self.dead_players.clear()
        self.player_hold.clear()
        self.holding_med.clear()
        del self.med_used[:]
        del self.power_used[:]
        del self.went_to_spec[:]

    def process_team_switch(self, player, team):
        if self.game.state in ["in_progress", "countdown"]:
            if team in ['red', 'blue']:
                if self.add_new and not self.countdown and not player.is_alive:
                    if player.steam_id in self.went_to_spec:
                        self.went_to_spec.remove(player.steam_id)
                        team_slot = 0 if team == "red" else 1
                        with self.lock:
                            self.dead_players[player.id] = time.time() + self.team_timeout[team_slot]
                        self.team_timeout[team_slot] += self.add_seconds
                    else:
                        minqlx.player_spawn(player.id)
                        self.give_power_up(player)
            else:
                if player.steam_id not in self.went_to_spec:
                    self.went_to_spec.append(player.steam_id)
                with self.lock:
                    if player.id in self.dead_players:
                        del self.dead_players[player.id]

    @minqlx.delay(9.8)
    def assign_items(self):
        if self.game.state in ["in_progress", "countdown"]:
            self.player_hold.clear()
            self.holding_med.clear()
            del self.med_used[:]
            del self.power_used[:]
            teams = self.teams()
            for player in teams["red"] + teams["blue"]:
                self.give_power_up(player)

    @minqlx.next_frame
    def give_power_up(self, player):
        rand = random.random()
        if rand < self.kamakazi:
            select = 37
        else:
            select = self.selections[random.randrange(self.length)]
        if player.id in self.med_used:
            self.med_used.remove(player.id)
        if player.id in self.power_used:
            self.power_used.remove(player.id)
        minqlx.set_holdable(player.id, select)
        self.player_hold[player.id] = select
        self.holding_med[player.id] = False
        if select == 34:
            player.flight(fuel=10000, max_fuel=10000, thrust=2500, refuel=0)

    def cmd_power(self, player, msg, channel):
        if len(msg) == 1:
            if self.game.state == "in_progress" and player.is_alive and not self.countdown:
                self.execute_power(player)
            if self.block_power:
                return minqlx.RET_STOP_ALL

    @minqlx.next_frame
    def execute_power(self, player):
        held = player.state.holdable
        if self.holding_med[player.id]:
            self.holding_med[player.id] = False
            if held is None:
                self.med_used.append(player.id)
            if player.id not in self.power_used:
                minqlx.set_holdable(player.id, 0)
                minqlx.set_holdable(player.id, self.player_hold[player.id])
        else:
            self.holding_med[player.id] = True
            if held is None:
                self.power_used.append(player.id)
            if player.id not in self.med_used:
                minqlx.set_holdable(player.id, 0)
                minqlx.set_holdable(player.id, 28)

    def player_died(self, player):
        if self.game.state == "in_progress":
            team = player.team
            death_time = time.time()
            team_slot = 0 if team == "red" else 1
            with self.lock:
                self.dead_players[player.id] = death_time + self.team_timeout[team_slot]
            self.team_timeout[team_slot] += self.add_seconds
            if not self.countdown:
                self.check_for_last(team)

    @minqlx.thread
    def check_for_last(self, team):
        teams = self.teams()
        count = 0
        for player in teams[team]:
            if player.is_alive:
                count += 1
        if count == 1:
            if team == "red":
                for p in teams["blue"]:
                    super().play_sound(self.hunt_sound, p)
            else:
                for p in teams["red"]:
                    super().play_sound(self.hunt_sound, p)

    @minqlx.thread
    def start_timer(self):
        count = 0
        current = time.time()
        while self.game.state in ["in_progress", "countdown"]:
            keys = []
            with self.lock:
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
                with self.lock:
                    for key, value in self.dead_players.items():
                        self.player(key).center_print("^4Respawn in ^1{} ^4seconds".format(int(value - current)))
