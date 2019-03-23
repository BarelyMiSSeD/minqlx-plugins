# This is an extension plugin  for minqlx.
# Copyright (C) 2019 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# This is a bot filling plugin for the minqlx admin bot.
# This plugin requires the server to be using the specqueue.py, version 2.06.3 or higher, plugin.
# The script will keep the server filled with qlx_botsMaxBots per team.
# It will kick bots when players join to allow real players to play.
# It will add bots back into the game if the teamsize goes below the qlx_botsMaxBots when someone
#  disconnects or spectates.
#
# This scripts purpose is to give newer or bored players a server to join and play even if no
#  one else is playing at the time.
#

"""
//set map the server will change to when the script is loaded if bot_enable isn't on
set qlx_botsMap "almostlost"
//set the maximum number of bots per team
set qlx_botsMaxBots "4"
//set weather to set a bot default level or to use the bots standard level set in BOT_DEFAULT_SKILLS
set qlx_botsUseDefaultSkills "1"
//use this skill level for all bots if qlx_botsUseDefaultSkills is set to "1"
set qlx_botsSkillLevel "3"
"""

import minqlx
from random import randint
import time
import re
from threading import Timer

VERSION = "1.5"

TEAM_BASED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "ad", "1f", "har")
NONTEAM_BASED_GAMETYPES = ("ffa", "race", "rr")
QUAKE_BOTS = ("Crash", "Ranger", "Phobos", "Mynx", "Orbb", "Sarge", "Bitterman", "Grunt", "Hossman", "Daemia",
              "Hunter", "Angel", "Gorre", "Klesk", "Slash", "Wrack", "Biker", "Lucy", "Patriot", "TankJr",
              "Anarki", "Stripe", "Razor", "Keel", "Visor", "Uriel", "Bones", "Sorlag", "Doom",
              "Major", "Xaero", "Demona", "James")
BOT_DEFAULT_SKILLS = (1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4,
                      5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5)


class bots(minqlx.Plugin):
    def __init__(self):
        # bots cvar(s)
        self.set_cvar_once("qlx_botsMap", "almostlost")
        self.set_cvar_once("qlx_botsMaxBots", "4")
        self.set_cvar_once("qlx_botsUseDefaultSkills", "1")
        self.set_cvar_once("qlx_botsSkillLevel", "3")

        # Minqlx bot Hooks
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("game_countdown", self.handle_game_countdown)
        self.add_hook("game_start", self.handle_game_start)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("map", self.handle_map)
        self.add_hook("round_countdown", self.handle_round_countdown)
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("round_end", self.handle_round_end)
        self.add_hook("team_switch_attempt", self.handle_team_switch_attempt, priority=minqlx.PRI_HIGHEST)
        self.add_hook("set_configstring", self.handle_set_config_string)
        self.add_hook("death", self.death_monitor)
        self.add_hook("console_print", self.handle_console_print)

        # Minqlx bot commands
        # self.add_command("bots", self.bots_settings)

        # Script Variables and lists
        self.used_bots = []
        self.quake_bots = dict(zip(QUAKE_BOTS, BOT_DEFAULT_SKILLS))
        self.checking_bots = [False, False, False]
        self.round_countdown = False
        self.kicking_bot = False
        self.kicking_bots = False
        self.max_bots = self.get_cvar("qlx_botsMaxBots", int) if\
            self.get_cvar("qlx_botsMaxBots", int) <= self.get_cvar("teamsize", int) else self.get_cvar("teamsize", int)
        self._queue = None
        self.bot_game_timer = None
        self.bot_map = True
        self.checking_not_bot_map = False
        self._bot_numbers = [0, 0, 0]

        # initialization commands
        self.check_server()

    def handle_new_game(self):
        if self._queue.queue_populated() > 0:
            self.kick_bot()

    def handle_game_countdown(self):
        if self._queue.queue_populated() > 0:
            self.kick_bot()

    def handle_game_start(self, data):
        if self._queue.queue_populated() > 0:
            self.kick_bot()

    def handle_game_end(self, data):
        self.kick_all_bots()

    def handle_map(self, mapname, factory):
        minqlx.console_print("^3Map Event: {}".format(mapname))
        self.bot_map = True
        self.checking_bots = [False, False, False]
        self.round_countdown = False
        self.kicking_bots = False
        self.checking_not_bot_map = False
        if self.bot_game_timer:
            self.bot_game_timer.cancel()
            self.bot_game_timer = None
        if self.get_cvar("bot_enable", bool):
            self.bot_game_timer = Timer(60, self.start_all_bots_game)
            self.bot_game_timer.start()
            bot_status = self.add_kick_bot()
            msg = ["nothing", "kick", "add"]
            minqlx.console_print("^3Bot Status: ^4{}".format(msg[bot_status]))
            if bot_status == 1:
                @minqlx.delay(2)
                def kick():
                    self.kick_bot()
                kick()
            elif bot_status == 2:
                @minqlx.delay(2)
                def add():
                    self.add_bots()
                add()

    def handle_round_countdown(self, round_num):
        self.round_countdown = True
        if self._queue.queue_populated() > 0:
            self.kick_bot()

    def handle_round_start(self, number):
        self.round_countdown = False
        if self._queue.queue_populated() > 0:
            self.kick_bot()

    def handle_round_end(self, data):
        if self._queue.queue_populated() > 0:
            self.kick_bot()

    def handle_player_disconnect(self, player, reason):
        if not self._queue.queue_populated() > 0 or not self.kicking_bots:
            @minqlx.delay(1)
            def add_a_bot():
                if self.bot_map:
                    self.add_bots()

            add_a_bot()
        if not self.bot_game_timer:
            self.bot_game_timer = Timer(60, self.start_all_bots_game)
            self.bot_game_timer.start()
        if not self.bot_map:
            self.non_bot_map()

    def handle_team_switch(self, player, old_team, new_team):
        if not self._queue.sarge_fix_active() and not self.kicking_bot:
            if new_team == "spectator" and not self._queue.queue_populated() > 0:
                self.add_bots()
            elif new_team != "spectator" and str(player.steam_id)[0] != "9":
                self.kick_bot(new_team)
        self.kicking_bot = False
        if not self.bot_game_timer:
            self.bot_game_timer = Timer(60, self.start_all_bots_game)
            self.bot_game_timer.start()

    def handle_team_switch_attempt(self, player, old_team, new_team):
        @minqlx.delay(0.5)
        def kick_a_bot():
            if self._queue.queue_populated() > 0:
                self.kicking_bot = True
                self.kick_bot()

        if new_team != "spectator" and str(player.steam_id)[0] != "9":  # re.sub(r"\^[0-9]", "", player.name) not in QUAKE_BOTS and
            kick_a_bot()
        elif new_team == "spectator" and not self._queue.queue_populated() > 0:
            self.add_bots()

    def handle_set_config_string(self, index, values):
        if "teamsize" in values:
            @minqlx.delay(0.5)
            def set_team_size():
                team_size = self.get_max_team_size()
                max_bots = self.get_cvar("qlx_botsMaxBots", int)
                target_bot_size = team_size if team_size < max_bots else max_bots
                if target_bot_size != self.max_bots:
                    old_size = self.max_bots
                    self.max_bots = target_bot_size
                    if target_bot_size < old_size:
                        self.check_for_extra_bots()
                    elif target_bot_size > old_size:
                        self.add_bots()
                    minqlx.console_print("^1Bots max bots per team has been set to {}".format(self.max_bots))
            set_team_size()

    def death_monitor(self, victim, killer, data):
        if self.game.state not in ["in_progress", "countdown"]:
            self.check_bots()

    def handle_console_print(self, text):
        if self.bot_map:
            # map_name = self.get_cvar("mapname")
            if "BotAISetupClient failed" in text or "Fatal:" in text and "aas" in text:
                self.kicking_bots = True
                self.bot_map = False
                minqlx.console_print(text)
                minqlx.console_print("^1Bots not supported on map {}. ^3Will attempt a map change if server is"
                                     " empty of real players.".format(self.get_cvar("mapname")))
                self.non_bot_map()

    # ==============================================
    #               Plugin functions
    # ==============================================
    # Returns 0 for no action needed, 1 for kick bots, and 2 for add bots
    def add_kick_bot(self):
        teams = self.teams()
        check_bots = []
        for player in teams["red"] + teams["blue"] + teams["free"]:
            if str(player.steam_id)[0] == "9":
                check_bots.append(player)
        if len(check_bots) > 0 and self._queue.queue_populated() > 0:
            return 1
        elif self.game.type_short in TEAM_BASED_GAMETYPES:
            if len(teams["red"]) < self.max_bots or len(teams["blue"]) < self.max_bots:
                return 2
        elif self.game.type_short in NONTEAM_BASED_GAMETYPES:
            if len(teams["free"]) < self.max_bots:
                return 2
        else:
            return 0

    @minqlx.delay(2)
    def non_bot_map(self):
        if self.checking_not_bot_map:
            return
        self.checking_not_bot_map = True
        num_players = len(self.players())
        for player in self.players():
            if str(player.steam_id)[0] == "9":
                player.kick()
                num_players -= 1
        if num_players == 0:
            self.bot_map = True
            minqlx.console_command("map {}".format(self.get_cvar("qlx_botsMap")))
        else:
            if self.add_kick_bot() == 2:
                self.non_bot_map_message()
                self._queue.update_bots([0, 0, 0])

    @minqlx.delay(8)
    def non_bot_map_message(self):
        self.center_print("^1This map does not support bots."
                          " If bots are desired change the map to one where bots are supported.")
        self.msg("^1This map does not support bots."
                 " If bots are desired change the map to one where bots are supported.")

    def start_all_bots_game(self):
        if self.game.state not in ["in_progress", "countdown"]:
            teams = self.teams()
            bot_players = []
            for player in teams["red"] + teams["blue"] + teams["free"]:
                if str(player.steam_id)[0] == "9":
                    bot_players.append(player)
            if len(bot_players) > 1 and len(bot_players) == len(teams["red"] + teams["blue"] + teams["free"]):
                minqlx.console_command("qlx {}allready".format(self.get_cvar("qlx_commandPrefix")))
        self.bot_game_timer = None

    @minqlx.thread
    def check_bots(self):
        if not self.bot_map:
            self.check_bots[1] = False
            return
        if self.checking_bots[1]:
            return
        self.checking_bots[1] = True
        teams = self.teams()
        check_bots = []
        for player in teams["red"] + teams["blue"] + teams["free"]:
            if str(player.steam_id)[0] == "9":
                check_bots.append(player)
        for bot in check_bots:
            if bot.stats.damage_dealt > 50000:
                bot.kick()
                time.sleep(2)
        self.checking_bots[1] = False

    def get_max_team_size(self):
        max_team_size = self.get_cvar("teamsize", int)
        if max_team_size == 0:
            max_team_size = self.get_cvar("sv_maxClients", int)
            if self.game.type_short in TEAM_BASED_GAMETYPES:
                max_team_size /= 2
        return max_team_size

    @minqlx.delay(3)
    def check_server(self):
        def unload():
            minqlx.console_print("^1The specqueue script, version 2.06.6 or higher, is required for the bots script."
                                 " Include specqueue in the server configuration to use the bots script.")
            self.msg("^1The specqueue script, version 2.06.6 or higher, is required for the bots script."
                     " Include specqueue in the server configuration to use the bots script.")
            minqlx.console_command("qlx {}unload {}"
                                   .format(self.get_cvar("qlx_commandPrefix"), self.__class__.__name__))

        if "specqueue" not in minqlx.Plugin._loaded_plugins:
            unload()
            return
        self._queue = minqlx.Plugin._loaded_plugins["specqueue"]
        try:
            queue_version = self._queue.get_version()
        except AttributeError:
            unload()
            return
        version_list = queue_version.split(".")
        old_version = False
        if int(version_list[0]) < 2:
            old_version = True
        elif int(version_list[0]) == 2 and int(version_list[1]) < 6:
            old_version = True
        elif int(version_list[0]) == 2 and int(version_list[1]) == 6 and int(version_list[2]) < 6:
            old_version = True
        if old_version:
            unload()
            return
        if not self.get_cvar("bot_enable", bool):
            minqlx.console_command("set bot_enable 1")
            minqlx.console_command("map {}".format(self.get_cvar("qlx_botsMap")))
        else:
            self.add_bots()
            Timer(60, self.start_all_bots_game).start()

    @minqlx.thread
    def add_bots(self):
        if not self.bot_map:
            self.check_bots[0] = False
            return
        if self.checking_bots[1] or self.checking_bots[2]:
            Timer(2, self.add_bots).start()
            return
        if self.checking_bots[0] or self.kicking_bots:
            return
        self.checking_bots[0] = True
        skill_level = self.get_cvar("qlx_botsSkillLevel", int) if self.get_cvar("qlx_botsUseDefaultSkills", bool)\
            else 0
        add = True
        teams = self.teams()
        red = len(teams["red"])
        blue = len(teams["blue"])
        free = len(teams["free"])
        if self.game.type_short in TEAM_BASED_GAMETYPES:
            while add:
                if not self.bot_map:
                    return
                try:
                    if blue < self.max_bots and blue <= red:
                        team = "^4blue"
                    elif red < self.max_bots:
                        team = "^1red"
                    else:
                        add = False
                        continue
                    bot_selection = self.get_bot()
                    level = skill_level if skill_level > 0 else self.quake_bots[bot_selection]
                    minqlx.console_print("^3adding bot {} at skill level {} to {}"
                                         .format(bot_selection, skill_level, team))
                    minqlx.console_command("addbot {} {} {}".format(bot_selection, level, team))
                    red = red + 1 if team == "^1red" else red
                    blue = blue + 1 if team == "^4blue" else blue
                except Exception as e:
                    minqlx.console_print("^2Bots Add_Bots to teams Exception: {}".format(e))
                # time.sleep(0.2)
        elif self.game.type_short in NONTEAM_BASED_GAMETYPES:
            while add:
                if not self.bot_map:
                    return
                try:
                    if free < self.max_bots:
                        bot_selection = self.get_bot()
                        level = skill_level if skill_level > 0 else self.quake_bots[bot_selection]
                        minqlx.console_print("^1adding bot {} at skill level {}"
                                             .format(bot_selection, level))
                        minqlx.console_command("addbot {} {}".format(bot_selection, skill_level))
                        free += 1
                    else:
                        add = False
                except Exception as e:
                    minqlx.console_print("^2Bots Add_Bots to free Exception: {}".format(e))
                # time.sleep(0.2)
        time.sleep(1)
        self.update_bot_count()

        self.checking_bots[0] = False

    def update_bot_count(self):
        teams = self.teams()
        count = 0
        if len(teams["red"]) < 5:
            for player in teams["red"]:
                if str(player.steam_id)[0] == "9":
                    count += 1
        self._bot_numbers[0] = count
        count = 0
        if len(teams["blue"]) < 5:
            for player in teams["blue"]:
                if str(player.steam_id)[0] == "9":
                    count += 1
        self._bot_numbers[1] = count
        count = 0
        if len(teams["free"]) < 5:
            for player in teams["free"]:
                if str(player.steam_id)[0] == "9":
                    count += 1
        self._bot_numbers[2] = count

        self._queue.update_bots(self._bot_numbers)

    @minqlx.thread
    def check_for_extra_bots(self):
        if not self.bot_map:
            self.check_bots[2] = False
            return
        if self.checking_bots[2]:
            return
        self.checking_bots[2] = True
        teams = self.teams()
        if self.game.type_short in TEAM_BASED_GAMETYPES:
            red = []
            blue = []
            for player in teams["red"]:
                if str(player.steam_id)[0] == "9":
                    red.append(player)
            if len(teams["red"]) > self.max_bots and len(red) > 0:
                count = 0
                while True:
                    lowest_bot = red[0]
                    lowest_score = red[0].score
                    for bot in red:
                        if bot.score < lowest_score:
                            lowest_bot = bot
                    lowest_bot.kick()
                    red.remove(lowest_bot)
                    count += 1
                    if len(red) == 0 or len(teams["red"]) - count == self.max_bots:
                        break
            for player in teams["blue"]:
                if str(player.steam_id)[0] == "9":
                    blue.append(player)
            if len(teams["blue"]) > self.max_bots and len(blue) > 0:
                count = 0
                while True:
                    lowest_bot = blue[0]
                    lowest_score = blue[0].score
                    for bot in blue:
                        if bot.score < lowest_score:
                            lowest_bot = bot
                    lowest_bot.kick()
                    blue.remove(lowest_bot)
                    count += 1
                    if len(blue) == 0 or len(teams["blue"]) - count == self.max_bots:
                        break
        elif self.game.type_short in NONTEAM_BASED_GAMETYPES:
            check_bots = []
            for player in teams["free"]:
                if str(player.steam_id)[0] == "9":
                    check_bots.append(player)
            for bot in check_bots:
                if bot.stats.damage_dealt > 50000:
                    bot.kick()
        self.checking_bots[2] = False

        self.update_bot_count()

    def get_bot(self):
        selections = [x for x in range(0, len(QUAKE_BOTS)) if QUAKE_BOTS[x] not in self.used_bots]
        if len(selections) == 0:
            self.used_bots.clear()
            selections = [x for x in range(0, len(QUAKE_BOTS)) if QUAKE_BOTS[x] not in self.used_bots]
            teams = self.teams()
            for player in teams["red"] + teams["blue"] + teams["free"]:
                if str(player.steam_id)[0] == "9":
                    selections.remove(self.quake_bots[re.sub(r"\^[0-9]", "", player.name)])
                    self.used_bots.append(re.sub(r"\^[0-9]", "", player.name))
        bot = QUAKE_BOTS[selections[randint(0, len(selections))]]
        self.used_bots.append(bot)
        return bot

    @minqlx.thread
    def kick_bot(self, team=None):
        teams = self.teams()
        if team:
            if team == "red" or team == "blue" or team == "free":
                team_bots = []
                for player in teams["{}".format(team)]:
                    if str(player.steam_id)[0] == "9":
                        team_bots.append(player)
                if len(team_bots) == 0:
                    return
                score = team_bots[0].score
                bot = team_bots[0]
                for player in team_bots:
                    if player.score < score:
                        bot = player
                        score = player.score
                bot.kick()
        elif self.game.type_short in TEAM_BASED_GAMETYPES:
            red = []
            blue = []
            for player in teams["red"]:
                if str(player.steam_id)[0] == "9":
                    red.append(player)
            for player in teams["blue"]:
                if str(player.steam_id)[0] == "9":
                    blue.append(player)
            waiting_players = self._queue.queue_populated()
            while waiting_players > 0:
                if len(red + blue) == 0:
                    return
                if len(blue) > 0 and len(blue) >= len(red):
                    score = blue[0].score
                    bot = blue[0]
                    for player in blue:
                        if player.score < score:
                            bot = player
                            score = player.score
                    if self.round_countdown and bot.is_alive:
                        self.msg("^3Bot will be kicked during next round countdown to make room for the human player.")
                        return
                    else:
                        self.round_countdown = False
                        blue.remove(bot)
                        waiting_players -= 1
                        bot.kick()
                elif len(red) > 0:
                    score = red[0].score
                    bot = red[0]
                    for player in red:
                        if player.score < score:
                            bot = player
                            score = player.score
                    if self.round_countdown and bot.is_alive:
                        self.msg("^3Bot will be kicked during next round countdown to make room for the human player.")
                        return
                    else:
                        self.round_countdown = False
                        red.remove(bot)
                        waiting_players -= 1
                        bot.kick()
        elif self.game.type_short in NONTEAM_BASED_GAMETYPES:
            free = []
            for player in teams["free"]:
                if str(player.steam_id)[0] == "9":
                    free.append(player)
            if len(free) > 0:
                score = free[0].score
                bot = free[0]
                for player in free:
                    if player.score < score:
                        bot = player
                        score = player.score
                bot.kick()
        self._queue.check_for_opening(0.2)

        self.update_bot_count()

    @minqlx.delay(2)
    def kick_all_bots(self):
        self.kicking_bots = True
        for player in self.players():
            if str(player.steam_id)[0] == "9":
                player.kick()
