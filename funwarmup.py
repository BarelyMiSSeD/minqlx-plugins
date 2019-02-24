# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should review a copy of the GNU General Public License
# along with minqlx. See <http://www.gnu.org/licenses/>.

# This is a plugin for the minqlx admin bot.
# It modifies the game CVARs to make warmup time a little different and hopefully more fun.
# Be careful modifying the setting too much. Too many projectiles needing to be kept track of
#   by the server may result in server crashes. Use/Modify this at your own risk.

"""
//script cvars to be put in server configuration file (default: server.cfg). Default values shown.
// set the permission level for admins to allow setting and unsetting of the fun warm up mode
set qlx_fwAdminLevel "3"
// Enable or Disable the automatic enabling of the fun warm up mode during warmup
set qlx_fwSetupWarmupFun "1"
// Set the number of seconds each weapon is used during the fun warm up period
set qlx_fwInterval "60"
// Set the number of players allowed on the server to choose if the fun warm up uses WEAPONS or WEAPONS2 settings
// It looks at teamsize or maxplayers to determine which to use.
set qlx_fwPlayerSplit "8"
// This will either load the default settings from the server settings (set to "1"). Use for other than ca game types.
//  Or it will use the default settings in the script, which are based on clan arena (set to "0")
set qlx_fwLoadDefaultCvars "1"
"""

import minqlx
import random
from threading import Timer

VERSION = "2.6"


class funwarmup(minqlx.Plugin):
    def __init__(self):
        self.set_cvar_once("qlx_fwAdminLevel", "3")
        self.set_cvar_once("qlx_fwSetupWarmupFun", "1")
        self.set_cvar_once("qlx_fwInterval", "60")
        self.set_cvar_once("qlx_fwPlayerSplit", "8")
        self.set_cvar_once("qlx_fwLoadDefaultCvars", "1")

        self.add_hook("map", self.handle_map)
        self.add_hook("game_countdown", self.handle_game_countdown)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_hook("player_spawn", self.handle_player_spawn)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("vote_ended", self.handle_vote_ended)
        self.add_hook("console_print", self.handle_console_print)
        self.add_hook("command", self.handle_command, priority=minqlx.PRI_HIGHEST)

        self.add_command("setfun", self.cmd_set_fun, self.get_cvar("qlx_fwAdminLevel", int))
        self.add_command("unsetfun", self.cmd_unset_fun, self.get_cvar("qlx_fwAdminLevel", int))
        self.add_command("weapon", self.cmd_weapon)
        self.add_command("dicts", self.dicts)

        self.fw_active = False
        self.fw_weapons = []
        self.cycle = None
        self.fw_interval = self.get_cvar("qlx_fwInterval", int)
        self.fw_id = None
        self._game_type = self.game.type_short

        # Weapon Names
        self.WEAPON_NAMES = ["Rail Gun", "Shotgun", "Machine Gun", "Heavy Machine Gun", "Plasma Gun", "Rocket Launcher"]

        # settings variables
        self.PLAYER_CVARS = []
        self.PLAYER_DFLT_CVARS = []
        self.WEAPONS = {}
        self.WEAPONS2 = {}
        self.WEAPONS_DFLTS = {}
        self.DFLT_CVARS = []

        # Get default settings
        self.get_defaults()

    def get_defaults(self):
        # Player Settings
        self.PLAYER_CVARS = ["g_infiniteAmmo 1", "g_startingWeapons 8447", "g_startingArmor 300",
                             "g_startingHealth 500"]
        if self.get_cvar("qlx_fwLoadDefaultCvars", bool):
            self.PLAYER_DFLT_CVARS = []
            get_cvars = ["g_infiniteAmmo", "g_startingWeapons", "g_startingArmor", "g_startingHealth"]
            for cvar in get_cvars:
                self.PLAYER_DFLT_CVARS.append("{} {}".format(cvar, self.get_cvar(cvar)))
        else:
            self.PLAYER_DFLT_CVARS = ["g_infiniteAmmo 0", "g_startingWeapons 8447", "g_startingArmor 100",
                                      "g_startingHealth 200"]
        # Weapon Fun CVARs
        self.WEAPONS = {
            0: ["weapon_reload_rg 80", "g_knockback_rg 0.45", "g_railJump 1"],
            1: ["weapon_reload_sg 150", "g_knockback_sg 0.45"],
            2: ["weapon_reload_mg 20", "g_knockback_mg 0.25"],
            3: ["weapon_reload_hmg 25", "g_knockback_hmg 0.25"],
            4: ["weapon_reload_pg 40", "g_knockback_pg 0.25", "g_knockback_pg_self 2.60", "g_velocity_pg 20000"],
            5: ["weapon_reload_rl 200", "g_knockback_rl 0.45", "g_knockback_rl_self 2.20", "g_velocity_rl 20000"]
        }
        self.WEAPONS2 = {
            0: ["weapon_reload_rg 200", "g_knockback_rg 0.45", "g_railJump 1"],
            1: ["weapon_reload_sg 300", "g_knockback_sg 0.45"],
            2: ["weapon_reload_mg 40", "g_knockback_mg 0.25"],
            3: ["weapon_reload_hmg 45", "g_knockback_hmg 0.25"],
            4: ["weapon_reload_pg 60", "g_knockback_pg 0.25", "g_knockback_pg_self 2.60", "g_velocity_pg 20000"],
            5: ["weapon_reload_rl 300", "g_knockback_rl 0.45", "g_knockback_rl_self 2.20", "g_velocity_rl 20000"]
        }
        # Weapon Default CVARs
        if self.get_cvar("qlx_fwLoadDefaultCvars", bool):
            self.WEAPONS_DFLTS = {}
            get_dflts = {
                0: ["weapon_reload_rg", "g_knockback_rg", "g_railJump"],
                1: ["weapon_reload_sg", "g_knockback_sg", "g_range_sg_falloff"],
                2: ["weapon_reload_mg", "g_knockback_mg"],
                3: ["weapon_reload_hmg", "g_knockback_hmg"],
                4: ["weapon_reload_pg", "g_knockback_pg", "g_knockback_pg_self", "g_velocity_pg"],
                5: ["weapon_reload_rl", "g_knockback_rl", "g_knockback_rl_self", "g_velocity_rl"]
            }
            for weapon in range(0, 6):
                self.WEAPONS_DFLTS[weapon] = []
                for cvar in get_dflts[weapon]:
                    self.WEAPONS_DFLTS[weapon].append("{} {}".format(cvar, self.get_cvar(cvar)))
        else:
            self.WEAPONS_DFLTS = {
                0: ["weapon_reload_rg 1500", "g_knockback_rg 0.85", "g_railJump 0"],
                1: ["weapon_reload_sg 1000", "g_knockback_sg 1.00", "g_range_sg_falloff 768"],
                2: ["weapon_reload_mg 100", "g_knockback_mg 1.00"],
                3: ["weapon_reload_hmg 75", "g_knockback_hmg 1.00"],
                4: ["weapon_reload_pg 100", "g_knockback_pg 1.10", "g_knockback_pg_self 1.10", "g_velocity_pg 2000"],
                5: ["weapon_reload_rl 800", "g_knockback_rl 0.90", "g_knockback_rl_self 1.10", "g_velocity_rl 1000"]
            }
        # Default CVARs
        if self.get_cvar("qlx_fwLoadDefaultCvars", bool):
            self.DFLT_CVARS = []
            load_cvars = ["g_infiniteAmmo", "g_startingWeapons", "g_startingArmor", "g_startingHealth",
                          "weapon_reload_rl", "weapon_reload_pg", "weapon_reload_rg",
                          "weapon_reload_lg", "weapon_reload_sg", "weapon_reload_gl",
                          "weapon_reload_mg", "weapon_reload_hmg", "g_velocity_rl", "g_velocity_pg",
                          "g_velocity_gl", "g_knockback_rl", "g_knockback_pg", "g_knockback_rg",
                          "g_knockback_lg", "g_knockback_sg", "g_knockback_gl", "g_knockback_mg",
                          "g_knockback_hmg", "g_knockback_rl_self", "g_railJump", "g_velocity_pg",
                          "g_velocity_rl"]
            for cvar in load_cvars:
                self.DFLT_CVARS.append("{} {}".format(cvar, self.get_cvar(cvar)))
        else:
            self.DFLT_CVARS = ["g_infiniteAmmo 0", "g_startingWeapons 8447", "g_startingArmor 100",
                               "g_startingHealth 200", "weapon_reload_rl 800", "weapon_reload_pg 100",
                               "weapon_reload_rg 1500", "weapon_reload_lg 50", "weapon_reload_sg 1000",
                               "weapon_reload_gl 800", "weapon_reload_mg 100", "weapon_reload_hmg 75",
                               "g_velocity_rl 1000", "g_velocity_pg 2000", "g_velocity_gl 700", "g_knockback_rl 0.90",
                               "g_knockback_pg 1.10", "g_knockback_rg 0.85", "g_knockback_lg 1.75",
                               "g_knockback_sg 1.00", "g_knockback_gl 1.10", "g_knockback_mg 1.00",
                               "g_knockback_hmg 1.00", "g_knockback_rl_self 1.10", "g_railJump 0", "g_velocity_pg 2000",
                               "g_velocity_rl 1000"]
        return True

    def handle_vote_ended(self, votes, vote, args, passed):
        if passed and vote.lower() == "map":
            self.set_normal_mode()

    def handle_console_print(self, text):
        if text.startswith("zmq RCON command"):
            args = text.split(":")
            if args[1].startswith(" map "):
                self.set_normal_mode()

    def handle_command(self, caller, command, args):
        args_list = args.split(" ")
        if args_list[0].endswith("map"):
            self.set_normal_mode()

    def handle_map(self, mapname, factory):
        got_defaults = False
        if self._game_type != self.game.type_short:
            got_defaults = self.get_defaults()
        if got_defaults:
            if self.fw_active:
                self.set_normal_mode()
            if self.get_cvar("qlx_fwSetupWarmupFun", bool):
                Timer(2, self.start_fun_warm_up).start()
        self._game_type = self.game.type_short

    def handle_game_countdown(self):
        self.set_normal_mode()

    def handle_player_disconnect(self, player, reason):
        self.disconnect_action()

    @minqlx.delay(1)
    def disconnect_action(self):
        teams = self.teams()
        if self.fw_active and (len(self.players()) == 0 or len(teams["red"] + teams["blue"] + teams["free"]) == 0):
            self.set_normal_mode()

    def handle_player_loaded(self, player):
        if self.fw_active:
            player.center_print("^6Fun Warmup mode is ^1ON")
            if len(self.fw_weapons) > 0:
                player.center_print("^2Fun Warmup weapon is ^1{} \n^2^1{} ^2seconds of fun per weapon."
                                    .format(self.WEAPON_NAMES[self.fw_weapons[-1]], self.fw_interval))

    def handle_player_spawn(self, player):
        if self.fw_active:
            if player.team != "spectator":
                if len(self.fw_weapons) > 0:
                    player.tell("^2Fun Warmup weapon is ^1{}".format(self.WEAPON_NAMES[self.fw_weapons[-1]]))
                else:
                    player.tell("^6Fun Warmup mode is ^1ON")
            else:
                teams = self.teams()
                if len(teams["red"] + teams["blue"] + teams["free"]) == 0:
                    self.set_normal_mode()
        elif self.get_cvar("qlx_fwSetupWarmupFun", bool) and self.game.state == "warmup":
            Timer(0.2, self.start_fun_warm_up).start()

    def handle_game_end(self, data):
        if data["ABORTED"]:
            if self.get_cvar("qlx_fwSetupWarmupFun", bool):
                Timer(2, self.start_fun_warm_up).start()

    def start_fun_warm_up(self):
        teams = self.teams()
        if not self.fw_active and len(teams["red"] + teams["blue"] + teams["free"]) > 0:
            self.set_fun_warm_up()

    def cmd_set_fun(self, player, msg, channel):
        if self.game.state == "warmup":
            if not self.fw_active:
                self.set_fun_warm_up()
        else:
            player.msg("^1The game is not in warmup. Changes not allowed.")

    def cmd_unset_fun(self, player, msg, channel):
        self.set_normal_mode()

    def cmd_weapon(self, player, msg, channel):
        if self.fw_active:
            if len(self.fw_weapons) > 0:
                self.msg("^2Fun Warmup weapon is ^1{}".format(self.WEAPON_NAMES[self.fw_weapons[-1]]))
            else:
                self.msg("^3No Fun Warmup weapon is set.")
        else:
            self.msg("^6Fun Warmup mode is ^3OFF")

    def set_fun_warm_up(self):
        self.fw_active = True
        self.fw_weapons = []
        for setting in self.PLAYER_CVARS:
            minqlx.console_command("set {}".format(setting))
        fw_id = self.fw_id = random.randint(0, 10000000)
        self.cycle_fun_weapons(fw_id)

    @minqlx.thread
    def cycle_fun_weapons(self, fw_id=None):
        if self.fw_active and self.game.state == "warmup" and fw_id == self.fw_id:
            for used in self.fw_weapons:
                cvar_list = self.WEAPONS_DFLTS[used]
                for cvar in cvar_list:
                    minqlx.console_command("set {}".format(cvar))
            max_players = self.get_max_players()
            if len(self.fw_weapons) >= len(self.WEAPON_NAMES):
                self.fw_weapons = []
            numbers = [n for n in range(0, len(self.WEAPON_NAMES))]
            numbers = [n for n in numbers if n not in self.fw_weapons]
            choice = random.choice(numbers)
            self.fw_weapons.append(choice)
            if max_players <= self.get_cvar("qlx_fwPlayerSplit", int):
                minqlx.console_print("Using WEAPONS settings for {}".format(self.WEAPON_NAMES[choice]))
                for setting in self.WEAPONS[choice]:
                    minqlx.console_command("set {}".format(setting))
            else:
                minqlx.console_print("Using WEAPONS2 settings for {}".format(self.WEAPON_NAMES[choice]))
                for setting in self.WEAPONS2[choice]:
                    minqlx.console_command("set {}".format(setting))
            players = self.players()
            for player in players:
                player.center_print("^2Fun Warmup weapon is ^1{} \n^2for the next ^1{} ^2seconds."
                                    .format(self.WEAPON_NAMES[choice], self.fw_interval))
            self.msg("^2Fun Warmup weapon is ^1{} ^2for the next ^1{} ^2seconds."
                     .format(self.WEAPON_NAMES[self.fw_weapons[-1]], self.fw_interval))
            Timer(self.fw_interval, self.cycle_fun_weapons, [fw_id]).start()
        elif not self.fw_active:
            self.set_normal_mode()

    def set_normal_mode(self):
        msg = False
        if self.fw_active:
            msg = True
        self.fw_active = False
        minqlx.console_print("Fun Warm Up: Setting normal mode.")
        if msg:
            for player in self.players():
                player.center_print("^6Fun Warmup mode is ^3OFF")
                player.tell("^6Fun Warmup mode is ^3OFF")
        self.fw_weapons = []
        for setting in self.DFLT_CVARS:
            minqlx.console_command("set {}".format(setting))

    def get_max_players(self):
        max_players = self.get_cvar("teamsize", int)
        if max_players == 0:
            max_players = self.get_cvar("sv_maxClients", int)
        else:
            max_players = max_players * 2
        return max_players

    def dicts(self, player, msg, channel):
        minqlx.console_print(str(self.DFLT_CVARS))
