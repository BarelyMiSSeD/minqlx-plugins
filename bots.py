# This is an extension plugin  for minqlx.
# Copyright (C) 2019 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# *** IMPORTANT !!!!! ***
# DO NOT include specqueue in the qlx_plugins cvar value of your server config. This plugin loads specqueue
#  automatically. Put specqueue.py in the regular minqlx plugins directory with this plugin.

# This is a bot filling plugin for the minqlx admin bot.
# This plugin requires the server to be using the specqueue.py, version 2.08.4 or higher, plugin.
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
// 0=use qlx_botsSkillLevel, 1=use BOT_DEFAULT_SKILLS
set qlx_botsUseBotDefaultSkills "0"
//use this skill level for all bots if qlx_botsUseBotDefaultSkills is set to "0"
set qlx_botsSkillLevel "3.5"
// Enable to have the bots play games (0=disable, 1=enable)
set qlx_botsBotOnlyGames "1"
"""

import minqlx
from random import randint
import re
from threading import Timer
import time
from .specqueue import specqueue

BOT_VERSION = "2.4"

TEAM_BASED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "ad", "1f", "har")
NONTEAM_BASED_GAMETYPES = ("ffa", "race", "rr")
SUPPORTED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "ad", "1f", "har", "ffa", "race", "rr")

QUAKE_BOTS = {"Crash": [1, "crash"], "Ranger": [1, "ranger"], "Phobos": [1, "doom/phobos"], "Mynx": [1, "mynx"],
              "Orbb": [1, "orbb"], "Sarge": [1, "sarge"], "Bitterman": [2, "bitterman"], "Grunt": [2, "grunt"],
              "Hossman": [2, "biker/hossman"], "Daemia": [2, "major/daemia"], "Hunter": [2, "hunter"],
              "Angel": [3, "lucy/angel"], "Gorre": [3, "visor/gorre"], "Klesk": [3, "klesk"], "Slash": [3, "slash"],
              "Wrack": [3, "ranger/wrack"], "Biker": [4, "biker"], "Lucy": [4, "lucy"], "Patriot": [4, "razor/patriot"],
              "TankJr": [4, "tankjr"], "Anarki": [4, "anarki"], "Stripe": [5, "grunt/stripe"], "Razor": [5, "razor"],
              "Keel": [5, "keel"], "Visor": [5, "visor"], "Uriel": [5, "uriel"], "Bones": [5, "bones"],
              "Sorlag": [5, "sorlag"], "Doom": [5, "doom"], "Major": [5, "major"], "Xaero": [5, "xaero"],
              "Demona": [5, "major/red"], "James": [5, "james"], "Trainer": [1, "crash/trainer"],
              "Flynn": [5, "doom/junglestorm"], "Mace": [5, "doom/redstorm"], "Bryson": [5, "doom/desertstorm"],
              "McCormick": [5, "doom/urbanstorm"], "Dre": [2, "dre"], "Eminem": [2, "eminem"], "Blisk": [2, "klesk"],
              "Gormog": [2, "sorlag"], "Helion": [2, "doom/blue"], "Huntress": [2, "hunter"],
              "Valkyrie": [2, "hunter/harpy"], "Mu_v.1": [2, "major/mu_major"],
              "Mu_v.2": [2, "slash/mu_slash"]}  # Mu_v.3 doesn't seem to work


class bots(specqueue):
    def __init__(self):
        super().__init__()

        # bots cvar(s)
        self.set_cvar_once("qlx_botsMap", "almostlost")
        self.set_cvar_once("qlx_botsMaxBots", "4")
        self.set_cvar_once("qlx_botsUseBotDefaultSkills", "0")
        self.set_cvar_once("qlx_botsSkillLevel", "3.5")
        self.set_cvar_once("qlx_botsBotOnlyGames", "1")

        # Minqlx bot Hooks
        self.add_hook("new_game", self.bots_handle_new_game)
        self.add_hook("game_countdown", self.bots_handle_game_countdown)
        self.add_hook("game_start", self.bots_handle_game_start)
        self.add_hook("game_end", self.bots_handle_game_end)
        self.add_hook("player_disconnect", self.bots_handle_player_disconnect)
        self.add_hook("team_switch", self.bots_handle_team_switch)
        self.remove_hook("team_switch_attempt", self.handle_team_switch_attempt, priority=minqlx.PRI_HIGH)
        self.add_hook("team_switch_attempt", self.handle_team_switch_attempt, priority=minqlx.PRI_HIGH)
        self.add_hook("map", self.bots_handle_map)
        self.add_hook("round_countdown", self.bots_handle_round_countdown)
        self.add_hook("round_start", self.bots_handle_round_start)
        self.add_hook("round_end", self.bots_handle_round_end)
        self.add_hook("set_configstring", self.bots_handle_set_config_string)
        self.add_hook("console_print", self.bots_handle_console_print)
        self.add_hook("vote_ended", self.bots_handle_vote_ended)
        self.add_hook("player_loaded", self.bots_handle_player_loaded, priority=minqlx.PRI_LOWEST)

        # Minqlx bot commands
        self.add_command("setbots", self.set_bots, 3)

        # Script Variables and lists
        self.quake_bots = QUAKE_BOTS
        self.checking_bots = [False, False, False]
        self.kicking_bot = False
        self.kicking_bots = False
        self.max_bots = self.get_cvar("qlx_botsMaxBots", int) if\
            self.get_cvar("qlx_botsMaxBots", int) <= self.get_cvar("teamsize", int) else self.get_cvar("teamsize", int)
        self.user_max_bots = False
        self.bot_game_timer = None
        self.bot_map = True
        self.checking_not_bot_map = False
        self._bot_numbers = [0, 0, 0]
        self._avail_bots = []

        # initialization commands
        self.check_server()

    def bots_handle_new_game(self):
        if self._queue.size() > 0:
            self.kick_bot()

    def bots_handle_game_countdown(self):
        if self._queue.size() > 0:
            self.kick_bot()

    def bots_handle_game_start(self, data):
        if self._queue.size() > 0:
            self.kick_bot()

    def bots_handle_game_end(self, data):
        self.kick_all_bots()

    def bots_handle_map(self, mapname, factory):
        minqlx.console_print("^3Map Event: {}".format(mapname))
        self.bot_map = True
        self.checking_bots = [False, False, False]
        self.in_countdown = False
        self.kicking_bots = False
        self.checking_not_bot_map = False
        self.max_bots = self.get_cvar("qlx_botsMaxBots", int) if \
            self.get_cvar("qlx_botsMaxBots", int) <= self.get_cvar("teamsize", int) else self.get_cvar("teamsize", int)
        self.user_max_bots = False
        if self.bot_game_timer:
            self.bot_game_timer.cancel()
            self.bot_game_timer = None
        if self.get_cvar("bot_enable", bool):
            if self.get_cvar("qlx_botsBotOnlyGames", bool):
                self.bot_game_timer = Timer(60, self.start_all_bots_game)
                self.bot_game_timer.start()
            bot_status = self.needed_bot_action()
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

    def bots_handle_round_countdown(self, round_num):
        self.in_countdown = True
        if self._queue.size() > 0:
            self.kick_bot()

    def bots_handle_round_start(self, number):
        self.in_countdown = False
        if self._queue.size() > 0:
            self.kick_bot()

    def bots_handle_round_end(self, data):
        if self._queue.size() > 0:
            self.kick_bot()

    def bots_handle_player_disconnect(self, player, reason):
        if (not self._queue.size() > 0 or not self.kicking_bots) and self.bot_map:
            @minqlx.delay(0.5)
            def add_a_bot():
                self.add_bots()

            add_a_bot()
        if self.get_cvar("qlx_botsBotOnlyGames", bool) and self.game.state not in ["in_progress", "countdown"] and\
                not self.bot_game_timer:
            self.bot_game_timer = Timer(60, self.start_all_bots_game)
            self.bot_game_timer.start()
        if not self.bot_map:
            self.non_bot_map()

    def bots_handle_team_switch(self, player, old_team, new_team):
        if not self.kicking_bot:
            if new_team == "spectator" and not self._queue.size() > 0:
                self.add_bots()
            elif new_team != "spectator" and str(player.steam_id)[0] != "9":
                self.kick_bot(new_team)
        self.kicking_bot = False
        if self.get_cvar("qlx_botsBotOnlyGames", bool) and self.game.state not in ["in_progress", "countdown"] and\
                not self.bot_game_timer:
            self.bot_game_timer = Timer(60, self.start_all_bots_game)
            self.bot_game_timer.start()

    def handle_team_switch_attempt(self, player, old_team, new_team):
        try:
            if self.q_game_info[0] in SUPPORTED_GAMETYPES and new_team != "spectator" and old_team == "spectator":
                teams = self.teams()
                at_max_players = False
                join_locked = False
                if self.q_game_info[0] in TEAM_BASED_GAMETYPES:
                    if len(teams["red"]) + len(teams["blue"]) >= self.get_max_players():
                        at_max_players = True
                    join_locked = self.free_locked
                elif self.q_game_info[0] in NONTEAM_BASED_GAMETYPES:
                    if len(self.teams()["free"]) >= self.get_max_players():
                        at_max_players = True
                    join_locked = self.red_locked or self.blue_locked
                if self._queue.size() > 0 or join_locked or self.game.state in ["in_progress", "countdown"] or\
                        at_max_players:
                    if player.steam_id not in self._join:
                        self.add_to_join(player)
                    self.add_to_queue(player)
                    self.remove_from_spec(player)
                    self.check_for_opening(0.2)

                    @minqlx.delay(0.5)
                    def kick_a_bot():
                        if self._queue.size() > 0:
                            self.kicking_bot = True
                            self.kick_bot()

                    if new_team != "spectator" and str(player.steam_id)[0] != "9":
                        kick_a_bot()
                    elif new_team == "spectator" and not self._queue.size() == 0:
                        self.add_bots()

                    return minqlx.RET_STOP_ALL
        except Exception as e:
            minqlx.console_print("^1bots handle_team_switch_attempt Exception: {}".format(e))

    def bots_handle_set_config_string(self, index, values):
        if "teamsize" in values:
            @minqlx.delay(0.5)
            def set_team_size():
                team_size = self.get_max_team_size()
                max_bots = self.get_cvar("qlx_botsMaxBots", int) if not self.user_max_bots else self.max_bots
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

    def bots_handle_console_print(self, text):
        if self.bot_map:
            if "BotAISetupClient failed" in text or "Fatal:" in text and "aas" in text:
                self.kicking_bots = True
                self.bot_map = False
                minqlx.console_print(text)
                minqlx.console_print("^1Bots not supported on map {}. ^3Will attempt a map change if server is"
                                     " empty of real players.".format(self.get_cvar("mapname")))
                self.non_bot_map()

    def bots_handle_vote_ended(self, votes, vote, args, passed):
        if passed and vote == "map":
            self.kick_all_bots()

    def bots_handle_player_loaded(self, player):
        if self.game.state not in ["in_progress", "countdown"] and not self.bot_map:
            @minqlx.delay(1)
            def msg_player():
                player.tell("^1This map does not support bots."
                            " If bots are desired change the map to one where bots are supported.")
                player.center_print("^1This map does not support bots."
                                    " If bots are desired change the map to one where bots are supported.")
            msg_player()

    # ==============================================
    #               Plugin functions
    # ==============================================
    # Returns 0 for no action needed, 1 for kick bots, and 2 for add bots
    def needed_bot_action(self):
        teams = self.teams()
        check_bots = {"red": [], "blue": [], "free": []}
        for player in teams["red"]:
            if str(player.steam_id)[0] == "9":
                check_bots["red"].append(player)
        for player in teams["blue"]:
            if str(player.steam_id)[0] == "9":
                check_bots["blue"].append(player)
        for player in teams["free"]:
            if str(player.steam_id)[0] == "9":
                check_bots["free"].append(player)
        if len(check_bots["red"] + check_bots["blue"] + check_bots["free"]) > 0 and self._queue.size() > 0:
            return 1
        elif self.game.type_short in TEAM_BASED_GAMETYPES:
            if len(teams["red"]) < self.max_bots or len(teams["blue"]) < self.max_bots:
                return 2
            elif len(teams["red"]) > self.max_bots and len(check_bots["red"]) > 0 or\
                    len(teams["blue"]) > self.max_bots and len(check_bots["blue"]) > 0:
                return 1
            else:
                return 0
        elif self.game.type_short in NONTEAM_BASED_GAMETYPES:
            if len(teams["free"]) < self.max_bots:
                return 2
            elif len(teams["free"]) > self.max_bots and len(check_bots["free"]) > 0:
                return 1
            else:
                return 0
        else:
            return 0

    @minqlx.delay(2)
    def non_bot_map(self):
        if self.checking_not_bot_map:
            return
        self.checking_not_bot_map = True
        players = self.players()
        num_players = len(players)
        for player in players:
            if str(player.steam_id)[0] == "9":
                player.kick()
                num_players -= 1
        if num_players == 0:
            @minqlx.next_frame
            def map():
                minqlx.console_command("map {}".format(self.get_cvar("qlx_botsMap")))
            map()
        else:
            if self.needed_bot_action() == 2:
                self.non_bot_map_message()

    @minqlx.delay(12)
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
            minqlx.console_print("^1The specqueue script, version 2.08.4 or higher, is required for the bots script."
                                 " Include specqueue in the server configuration to use the bots script.")
            self.msg("^1The specqueue script, version 2.08.4 or higher, is required for the bots script."
                     " Include specqueue in the server configuration to use the bots script.")
            minqlx.console_command("qlx {}unload {}"
                                   .format(self.get_cvar("qlx_commandPrefix"), self.__class__.__name__))

        try:
            queue_version = self.specqueue_version()
        except AttributeError:
            unload()
            return
        version_list = queue_version.split(".")
        old_version = False
        if int(version_list[0]) < 2:
            old_version = True
        elif int(version_list[0]) == 2 and int(version_list[1]) < 8:
            old_version = True
        elif int(version_list[0]) == 2 and int(version_list[1]) == 8 and int(version_list[2]) < 4:
            old_version = True
        if old_version:
            unload()
            return
        self.reset_avail_bots()
        if not self.get_cvar("bot_enable", bool):
            minqlx.console_command("set bot_enable 1")
            minqlx.console_command("map {}".format(self.get_cvar("qlx_botsMap")))
        else:
            self.add_bots()
            Timer(60, self.start_all_bots_game).start()

    def reset_avail_bots(self):
        self._avail_bots = [key for key in self.quake_bots.keys()]

    @minqlx.thread
    def add_bots(self):
        if not self.bot_map:
            self.checking_bots[0] = False
            return
        if self.checking_bots[1] or self.checking_bots[2]:
            Timer(2, self.add_bots).start()
            return
        if self.checking_bots[0] or self.kicking_bots:
            return
        self.checking_bots[0] = True
        skill_level = self.get_cvar("qlx_botsSkillLevel", float) if\
            not self.get_cvar("qlx_botsUseBotDefaultSkills", bool) else 0
        add = True
        teams = self.teams()
        red = len(teams["red"])
        blue = len(teams["blue"])
        free = len(teams["free"])
        bot_selection = None
        team = None
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
                    level = skill_level if skill_level > 0 else self.quake_bots[bot_selection][0]
                    self.add_bot(bot_selection, level, team)
                    red = red + 1 if team == "^1red" else red
                    blue = blue + 1 if team == "^4blue" else blue
                except Exception as e:
                    minqlx.console_print("^2Bots Add_Bots to teams Exception: {}".format(e))
                    minqlx.console_print("^3Bot: ^1{} ^3Level: ^1{} ^3Team: {}".format(bot_selection, skill_level, team))
        elif self.game.type_short in NONTEAM_BASED_GAMETYPES:
            while add:
                if not self.bot_map:
                    return
                try:
                    if free < self.max_bots:
                        bot_selection = self.get_bot()
                        level = skill_level if skill_level > 0 else self.quake_bots[bot_selection][0]
                        self.add_bot(bot_selection, level)
                        free += 1
                    else:
                        add = False
                except Exception as e:
                    minqlx.console_print("^2Bots Add_Bots to free Exception: {}".format(e))

        self.update_bot_count()
        self.checking_bots[0] = False

    @minqlx.next_frame
    def add_bot(self, bot, level, team="free"):
        minqlx.console_print("^3adding bot {} at skill level {} to {}".format(bot, level, team))
        minqlx.console_command("addbot {} {} {}".format(bot, level, team))

    def get_bot(self):
        if len(self._avail_bots) < 1:
            self.reset_avail_bots()
            teams = self.teams()
            for player in teams["red"] + teams["blue"] + teams["free"]:
                if str(player.steam_id)[0] == "9":
                    name = re.sub(r"\^[0-9]", "", player.name)
                    if name in self._avail_bots:
                        self._avail_bots.remove(name)
        return self._avail_bots.pop(randint(0, len(self._avail_bots) - 1))

    @minqlx.next_frame
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

    @minqlx.thread
    def check_for_extra_bots(self):
        if not self.bot_map:
            self.checking_bots[2] = False
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

    @minqlx.thread
    def kick_bot(self, team=None):
        self.kicking_bots = True
        teams = self.teams()
        if team:
            if team == "red" or team == "blue":
                if not self._queue.size() > 0 and len(teams["red"]) == len(teams["blue"]):
                    return
            elif team == "free":
                if not self._queue.size() > 0 and len(teams["free"]) <= self.get_max_team_size():
                    return
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
            self.update_bot_count()
            self.check_for_opening(0.5)
        elif self.game.type_short in TEAM_BASED_GAMETYPES:
            red = []
            blue = []
            for player in teams["red"]:
                if str(player.steam_id)[0] == "9":
                    red.append(player)
            for player in teams["blue"]:
                if str(player.steam_id)[0] == "9":
                    blue.append(player)
            waiting_players = self._queue.size()
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
                    if self.game.state == "in_progress" and not self.in_countdown and bot.is_alive:
                        self.msg("^3Bot will be kicked during next round countdown to make room for the human player.")
                        for player in teams["spectator"]:
                            player.center_print("^3Bot will be kicked during next round\n"
                                                "countdown to make room for the human player.")
                        return
                    else:
                        blue.remove(bot)
                        waiting_players -= 1
                        bot.kick()
                        self.update_bot_count()
                        self.check_for_opening(0.5)
                elif len(red) > 0:
                    score = red[0].score
                    bot = red[0]
                    for player in red:
                        if player.score < score:
                            bot = player
                            score = player.score
                    if self.game.state == "in_progress" and not self.in_countdown and bot.is_alive:
                        self.msg("^3Bot will be kicked during next round countdown to make room for the human player.")
                        for player in teams["spectator"]:
                            player.center_print("^3Bot will be kicked during next round\n"
                                                "countdown to make room for the human player.")
                        return
                    else:
                        red.remove(bot)
                        waiting_players -= 1
                        bot.kick()
                        self.update_bot_count()
                        self.check_for_opening(0.5)
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
                self.update_bot_count()
                self.check_for_opening(0.5)
        self.kicking_bots = False

    @minqlx.delay(0.5)
    def kick_all_bots(self):
        self.kicking_bots = True
        for player in self.players():
            if str(player.steam_id)[0] == "9":
                player.kick()

    @minqlx.thread
    def reset_players_models(self, msg=None):
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
                if str(pl.steam_id)[0] == "9":
                    name = re.sub(r"\^[0-9]", "", pl.name)
                    pl.model = self.quake_bots[name][1]
                elif pl.model:
                    pl.model = pl.model
                else:
                    pl.model = "sarge"
            return True
        except Exception as e:
            minqlx.console_print("^1bots reset_players_models Exception: {}".format(e))

    ###############################################
    #           In Game Client commands
    ###############################################
    def set_bots(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3A bot amount needs to be provided: ^1{}setbots <num> ^3(set to 0 to disable bots,"
                        " 'unset' to clear admin setting)"
                        .format(self.get_cvar("qlx_commandPrefix")))
        else:
            target_num = None
            if msg[1] == "unset":
                self.user_max_bots = False
                target_num = self.get_cvar("qlx_botsMaxBots", int) if\
                    self.get_cvar("qlx_botsMaxBots", int) <= self.get_cvar("teamsize", int) else\
                    self.get_cvar("teamsize", int)
            try:
                team_size = self.get_max_team_size()
                if not target_num:
                    target_num = int(msg[1])
                if target_num > team_size:
                    player.tell("^3The target bots can't be larger than the allowed players per team.")
                    return
                elif target_num == self.max_bots:
                    player.tell("^3The bots size is already {}.".format(target_num))
                    return
                self.max_bots = target_num
                self.user_max_bots = True
                action = self.needed_bot_action()
                minqlx.console_print("^6Action: {}".format(action))
                if action == 1:
                    self.check_for_extra_bots()
                    minqlx.console_print("^1Kicking Bot Due to max bots change")
                elif action == 2:
                    self.add_bots()
            except ValueError:
                player.tell("^3The amount must be an integer or 'unset'.")
