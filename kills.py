# This is an extension plugin  for minqlx.
# Copyright (C) 2016 mattiZed (github) aka mattiZed (ql)
# ** This plugin is thanks to mattiZed. Just modified EXTENSIVELY by BarelyMiSSeD
# to expand on the pummel counting and add other kill type monitors.
# It also adds end of match reports for the match,
# and total counts for each of the kill types when called.
#
# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this plugin. If not, see <http://www.gnu.org/licenses/>.

# This is a fun plugin written for Mino's Quake Live Server Mod minqlx.
# It displays "Killer x:y Victim" message when Victim gets a monitored kill
# and stores the information within REDIS DB
#
# Players can display their kill stats with:
#  "pummels" via !pummel or !gauntlet
#  "air gauntlets" via !airgauntlet
#  "grenades" via !grenades or !grenade
#  "air rockets" via !rockets or !rocket
#  "air plasma" via !plasma
#  "air rail" via !airrail
#  "telefrag" via !telefrag
#  "team telefrag" via !teamtele or !teamtelefrag
#  "speed kill" via !speed or !speedkill
# the Total displayed is all of that type kill and it displays kills for
# the victims that are on the server on the same time.
#
#
# **** CVAR Settings ****
# set qlx_killsPlaySounds "1"           : Turns the sound playing when a kill is made On/Off
# set qlx_killsSpeedMinimum "800"       : Sets the minimum speed needed to record a speed kill
# set qlx_killsMonitorKillTypes "511"   : Sets the types of kills that are monitored. See Below for settings.
#
# ******  How to set which kill types are recorded ******
# Add the values for each type of kill listed below and set that value
#  to the qlx_killsMonitorKillTypes in the same location as the rest of
#  your minqlx cvar's.
#
#  ****Kill Monitor Values****
#             Pummel:  1    (records any pummel/gauntlet kill)
#         Air Pummel:  2    (records any pummel/gauntlet kill where killer and victim are airborne)
#     Direct Grenade:  4    (records any kills with direct grenade hits)
#        Air Rockets:  8    (records any Air Rocket kills)
#         Air Plasma:  16   (records any Air Plasma kills)
#          Air Rails:  32   (records any Air Rails kills where both the killer and victim are airborne)
#           Telefrag:  64   (records any enemy telefrag)
#  Telefrag TeamKill:  128  (records any teamkill telefrag)
#         Speed Kill:  256
#
# The Default value is 'set qlx_killsMonitorKillTypes "511"' which enables
#  all the kill monitor types.

import minqlx

# DB related
PLAYER_KEY = "minqlx:players:{}"

# Add Game types here if this script is not working with your game type. Follow the format.
# Find your gametype in game with the !kgt or !killsgametype command.
SUPPORTED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "ffa", "ictf", "ad")


class kills(minqlx.Plugin):
    def __init__(self):
        self.set_cvar_once("qlx_killsMonitorKillTypes", "511")
        self.set_cvar_once("qlx_killsPlaySounds", "1")
        self.set_cvar_once("qlx_killsSpeedMinimum", "800")
        self.set_cvar_once("qlx_killsEndGameMsg", "1")

        self.add_hook("kill", self.handle_kill)
        self.add_hook("game_end", self.handle_end_game)
        self.add_hook("map", self.handle_map)
        self.add_hook("round_countdown", self.handle_round_count)
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("round_end", self.handle_round_end)

        self.add_command(("pummel", "gauntlet"), self.cmd_pummel)
        self.add_command(("airpummel", "airgauntlet"), self.cmd_airpummel)
        self.add_command(("grenades", "grenade"), self.cmd_grenades)
        self.add_command(("rockets", "rocket"), self.cmd_rocket)
        self.add_command("plasma", self.cmd_plasma)
        self.add_command(("airrail", "airrails"), self.cmd_airrail)
        self.add_command("telefrag", self.cmd_telefrag)
        self.add_command(("teamtelefrag", "teamtele"), self.cmd_teamtelefrag)
        self.add_command(("speed", "speedkill"), self.cmd_speedkill)
        self.add_command("speedlimit", self.cmd_speedlimit)
        self.add_command("kills_version", self.kills_version)
        self.add_command(("gametypes", "games"), self.supported_games)
        self.add_command("kills", self.kills_recorded)
        self.add_command(("kgt", "killsgametype"), self.cmd_kills_gametype, 3)
        self.add_command(("rkm", "reloadkillsmonitor"), self.cmd_kills_monitor, 3)

        self.kills_pummel = {}
        self.kills_airpummel = {}
        self.kills_grenades = {}
        self.kills_rockets = {}
        self.kills_plasma = {}
        self.kills_airrail = {}
        self.kills_telefrag = {}
        self.kills_teamtelefrag = {}
        self.kills_speed = {}

        self.kills_roundActive = 0

        self.kills_play_sounds = bool(self.get_cvar("qlx_killsPlaySounds"))
        self.kills_killMonitor = [0,0,0,0,0,0,0,0,0]
        self.cmd_kills_monitor()

        self.kills_gametype = self.game.type_short

    def handle_kill(self, victim, killer, data):
        try:
            if self.kills_gametype in SUPPORTED_GAMETYPES:
                mod = data["MOD"]
                msg = None
                if data["KILLER"]["SPEED"] > self.get_cvar("qlx_killsSpeedMinimum", int) and self.kills_killMonitor[8]:
                    if self.kills_play_sounds:
                        self.sound_play("sound/feedback/impact4")

                    if self.game.state == "in_progress":
                        killer_steam_id = killer.steam_id
                        victim_steam_id = victim.steam_id
                        self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":speedkill", str(victim_steam_id))
                        self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":speedkill:" + str(victim_steam_id))
                        speed_value = PLAYER_KEY.format(killer_steam_id) + ":highspeed"
                        if speed_value in self.db:
                            if int(data["KILLER"]["SPEED"]) > int(self.db[PLAYER_KEY.format(killer_steam_id) + ":highspeed"].split(".")[0]):
                                self.db[PLAYER_KEY.format(killer_steam_id) + ":highspeed"] = int(data["KILLER"]["SPEED"])
                        else:
                            self.db[PLAYER_KEY.format(killer_steam_id) + ":highspeed"] = int(data["KILLER"]["SPEED"])

                        killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":speedkill:" + str(victim_steam_id)]
                        victim_score = 0
                        if PLAYER_KEY.format(victim_steam_id) + ":speedkill:" + str(killer_steam_id) in self.db:
                            victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":speedkill:" + str(killer_steam_id)]

                        msg = "^1SPEED ^3{}^1! ^7{} ^1{}^7:^1{}^7 {}".format(int(data["KILLER"]["SPEED"]), killer.name, killer_score, victim_score, victim.name)
                        self.add_killer(str(killer.name), "SPEED")
                    else:
                        msg = "^1SPEED ^3{}^1! ^7{}^7 :^7 {} ^7(^3warmup^7)".format(int(data["KILLER"]["SPEED"]), killer.name, victim.name)

                elif mod == "GAUNTLET" and (self.kills_killMonitor[0] or self.kills_killMonitor[1]):
                    killed = data["VICTIM"]
                    kill = data["KILLER"]
                    if killed["AIRBORNE"] and kill["AIRBORNE"] and not killed["SUBMERGED"] and not kill["SUBMERGED"] and self.kills_killMonitor[1]:
                        if self.kills_play_sounds:
                            self.sound_play("sound/vo_evil/rampage2")

                        if self.game.state == "in_progress":
                            killer_steam_id = killer.steam_id
                            victim_steam_id = victim.steam_id
                            self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":airpummel", str(victim_steam_id))
                            self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":airpummel:" + str(victim_steam_id))

                            killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":airpummel:" + str(victim_steam_id)]
                            victim_score = 0
                            if PLAYER_KEY.format(victim_steam_id) + ":airpummel:" + str(killer_steam_id) in self.db:
                                victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":airpummel:" + str(killer_steam_id)]

                            msg = "^1AIR GAUNTLET!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score, victim.name)
                            self.add_killer(str(killer.name), "AIRGAUNTLET")
                        else:
                            msg = "^1AIR GAUNTLET!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                    elif self.kills_killMonitor[0]:
                        if self.kills_play_sounds:
                            self.sound_play("sound/vo_evil/humiliation1")

                        if self.game.state == "in_progress":
                            killer_steam_id = killer.steam_id
                            victim_steam_id = victim.steam_id
                            self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":pummeled", str(victim_steam_id))
                            self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":pummeled:" + str(victim_steam_id))

                            killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":pummeled:" + str(victim_steam_id)]
                            victim_score = 0
                            if PLAYER_KEY.format(victim_steam_id) + ":pummeled:" + str(killer_steam_id) in self.db:
                                victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":pummeled:" + str(killer_steam_id)]

                            msg = "^1PUMMEL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score, victim.name)
                            self.add_killer(str(killer.name), "GAUNTLET")
                        else:
                            msg = "^1PUMMEL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif mod == "GRENADE" and self.kills_killMonitor[2]:
                    if self.kills_play_sounds:
                        self.sound_play("sound/vo_female/holy_shit")

                    if self.game.state == "in_progress":
                        killer_steam_id = killer.steam_id
                        victim_steam_id = victim.steam_id
                        self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":grenaded", str(victim_steam_id))
                        self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":grenaded:" + str(victim_steam_id))

                        killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":grenaded:" + str(victim_steam_id)]
                        victim_score = 0
                        if PLAYER_KEY.format(victim_steam_id) + ":grenaded:" + str(killer_steam_id) in self.db:
                            victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":grenaded:" + str(killer_steam_id)]

                        msg = "^1GRENADE KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score, victim.name)
                        self.add_killer(str(killer.name), "GRENADE")
                    else:
                        msg = "^1GRENADE KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif mod == "ROCKET" and self.kills_killMonitor[3]:
                    killed = data["VICTIM"]
                    if killed["AIRBORNE"] and not killed["SUBMERGED"]:
                        if self.kills_play_sounds:
                            self.sound_play("sound/vo_evil/midair1")

                        if self.game.state == "in_progress":
                            killer_steam_id = killer.steam_id
                            victim_steam_id = victim.steam_id
                            self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":rocket", str(victim_steam_id))
                            self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":rocket:" + str(victim_steam_id))

                            killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":rocket:" + str(victim_steam_id)]
                            victim_score = 0
                            if PLAYER_KEY.format(victim_steam_id) + ":rocket:" + str(killer_steam_id) in self.db:
                                victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":rocket:" + str(killer_steam_id)]

                            msg = "^1AIR ROCKET KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score, victim.name)
                            self.add_killer(str(killer.name), "ROCKET")
                        else:
                            msg = "^1AIR ROCKET KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif mod == "PLASMA" and self.kills_killMonitor[4]:
                    killed = data["VICTIM"]
                    if killed["AIRBORNE"] and not killed["SUBMERGED"]:
                        if self.kills_play_sounds:
                            self.sound_play("sound/vo_evil/damage")

                        if self.game.state == "in_progress":
                            killer_steam_id = killer.steam_id
                            victim_steam_id = victim.steam_id
                            self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":plasma", str(victim_steam_id))
                            self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":plasma:" + str(victim_steam_id))

                            killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":plasma:" + str(victim_steam_id)]
                            victim_score = 0
                            if PLAYER_KEY.format(victim_steam_id) + ":plasma:" + str(killer_steam_id) in self.db:
                                victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":plasma:" + str(killer_steam_id)]

                            msg = "^1AIR PLASMA KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score, victim.name)
                            self.add_killer(str(killer.name), "PLASMA")
                        else:
                            msg = "^1AIR PLASMA KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif (mod == "RAILGUN" or mod == "RAILGUN_HEADSHOT") and self.kills_killMonitor[5]:
                    killed = data["VICTIM"]
                    kill = data["KILLER"]
                    if killed["AIRBORNE"] and kill["AIRBORNE"] and not killed["SUBMERGED"] and not kill["SUBMERGED"]:
                        if self.kills_play_sounds:
                            self.sound_play("sound/vo_female/midair3")

                        if self.game.state == "in_progress":
                            killer_steam_id = killer.steam_id
                            victim_steam_id = victim.steam_id
                            self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":airrail", str(victim_steam_id))
                            self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":airrail:" + str(victim_steam_id))

                            killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":airrail:" + str(victim_steam_id)]
                            victim_score = 0
                            if PLAYER_KEY.format(victim_steam_id) + ":airrail:" + str(killer_steam_id) in self.db:
                                victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":airrail:" + str(killer_steam_id)]

                            msg = "^1AIR RAIL KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score, victim.name)
                            self.add_killer(str(killer.name), "AIRRAIL")
                        else:
                            msg = "^1AIR RAIL KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif mod == "TELEFRAG" and self.kills_killMonitor[6] and not data["TEAMKILL"]:
                    if self.kills_play_sounds and (self.kills_roundActive or self.game.state == "warmup"):
                        self.sound_play("sound/vo/perforated")

                    if self.game.state == "in_progress" and self.kills_roundActive:
                        killer_steam_id = killer.steam_id
                        victim_steam_id = victim.steam_id
                        self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":telefrag", str(victim_steam_id))
                        self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":telefrag:" + str(victim_steam_id))

                        killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":telefrag:" + str(victim_steam_id)]
                        victim_score = 0
                        if PLAYER_KEY.format(victim_steam_id) + ":telefrag:" + str(killer_steam_id) in self.db:
                            victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":telefrag:" + str(killer_steam_id)]

                        msg = "^1TELEFRAG KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score, victim.name)
                        self.add_killer(str(killer.name), "TELEFRAG")
                    elif self.game.state != "in_progress" and not self.kills_roundActive:
                        msg = "^1TELEFRAG KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif mod == "TELEFRAG" and self.kills_killMonitor[7] and data["TEAMKILL"]:
                    if self.kills_play_sounds and (self.kills_roundActive or self.game.state == "warmup"):
                        self.sound_play("sound/vo_female/perforated")

                    if self.game.state == "in_progress" and self.kills_roundActive:
                        killer_steam_id = killer.steam_id
                        victim_steam_id = victim.steam_id
                        self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":teamtelefrag", str(victim_steam_id))
                        self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":teamtelefrag:" + str(victim_steam_id))

                        killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":teamtelefrag:" + str(victim_steam_id)]
                        victim_score = 0
                        if PLAYER_KEY.format(victim_steam_id) + ":teamtelefrag:" + str(killer_steam_id) in self.db:
                            victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":teamtelefrag:" + str(killer_steam_id)]

                        msg = "^6TEAM ^1TELEFRAG KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score, victim.name)
                        self.add_killer(str(killer.name), "TEAMTELEFRAG")
                    elif self.game.state != "in_progress" and not self.kills_roundActive:
                        msg = "^6TEAM ^1TELEFRAG KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                if msg:
                    self.msg(msg)
        except Exception as e:
            minqlx.console_print("^kills handle_kill Exception: {}".format(e))

    def handle_map(self, mapname, factory):
        self.kills_gametype = self.game.type_short

    def handle_round_count(self, round_number):
        self.kills_roundActive = 0

    def handle_round_start(self, round_number):
        self.kills_roundActive = 1

    def handle_round_end(self, round_number):
        self.kills_roundActive = 0

    def handle_end_game(self, data):
        if self.get_cvar("qlx_killsEndGameMsg", bool):
            try:
                self.kills_gametype = self.game.type_short
                if self.kills_gametype in SUPPORTED_GAMETYPES:
                    count = 0

                    msg = "^3Pummel ^1Killers^7: "
                    for k, v in self.kills_pummel.items():
                        msg += "{}^7:^1{}^7 ".format(k, v)
                        count += 1
                    if count > 0:
                        self.msg(msg)
                        count = 0

                    msg = "^3Air Gauntlet ^1Killers^7: "
                    for k, v in self.kills_airpummel.items():
                        msg += "{}^7:^1{}^7 ".format(k, v)
                        count += 1
                    if count > 0:
                        self.msg(msg)
                        count = 0

                    msg = "^3Grenade ^1Killers^7: "
                    for k, v in self.kills_grenades.items():
                        msg += "{}^7:^1{}^7 ".format(k, v)
                        count += 1
                    if count > 0:
                        self.msg(msg)
                        count = 0

                    msg = "^3Air Rocket ^1Killers^7: "
                    for k, v in self.kills_rockets.items():
                        msg += "{}^7:^1{}^7 ".format(k, v)
                        count += 1
                    if count > 0:
                        self.msg(msg)
                        count = 0

                    msg = "^3Air Plasma ^1Killers^7: "
                    for k, v in self.kills_plasma.items():
                        msg += "{}^7:^1{}^7 ".format(k, v)
                        count += 1
                    if count > 0:
                        self.msg(msg)
                        count = 0

                    msg = "^3Air Rail ^1Killers^7: "
                    for k, v in self.kills_airrail.items():
                        msg += "{}^7:^1{}^7 ".format(k, v)
                        count += 1
                    if count > 0:
                        self.msg(msg)
                        count = 0

                    msg = "^3Telefrag ^1Killers^7: "
                    for k, v in self.kills_telefrag.items():
                        msg += "{}^7:^1{}^7 ".format(k, v)
                        count += 1
                    if count > 0:
                        self.msg(msg)
                        count = 0

                    msg = "^3Team Telefrag ^1Killers^7: "
                    for k, v in self.kills_teamtelefrag.items():
                        msg += "{}^7:^1{}^7 ".format(k, v)
                        count += 1
                    if count > 0:
                        self.msg(msg)
                        count = 0

                    msg = "^3Speed ^1Killers^7: "
                    for k, v in self.kills_speed.items():
                        msg += "{}^7:^1{}^7 ".format(k, v)
                        count += 1
                    if count > 0:
                        self.msg(msg)
                        #count = 0

                    self.kills_pummel = {}
                    self.kills_airpummel = {}
                    self.kills_grenades = {}
                    self.kills_rockets = {}
                    self.kills_plasma = {}
                    self.kills_airrail = {}
                    self.kills_telefrag = {}
                    self.kills_teamtelefrag = {}
                    self.kills_speed = {}
            except Exception as e:
                minqlx.console_print("^kills handle_end_game Exception: {}".format(e))

    def cmd_kills_gametype(self, player, msg, channel):
        player.tell("^2The current gametype is \'{}\'".format(self.kills_gametype))
        return minqlx.RET_STOP_ALL

    def cmd_speedlimit(self, player, msg, channel):
        if self.kills_killMonitor[8]:
            self.msg("^3You need a speed of at least ^1{} ^3to register a speed kill.".format(self.get_cvar("qlx_killsSpeedMinimum")))
        else:
            self.msg("^4Speed Kill ^7stats are not enabled on this server.")

    def cmd_pummel(self, player, msg, channel):
        self.exec_cmd_pummel(player, msg, channel)

    @minqlx.thread
    def exec_cmd_pummel(self, player, msg, channel):
        if not self.kills_killMonitor[0]:
                self.msg("^4Pummel Kill ^7stats are not enabled on this server.")
        else:
            try:
                if len(msg) > 1:
                    player = self.player_id(msg[1], player)

                p_steam_id = player.steam_id
                total = 0
                pummels = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":pummeled")
                players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]

                msg = ""
                for p in pummels:
                    total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":pummeled:" + str(p)])
                    for pl in players:
                        if p == str(pl.steam_id):
                            count = self.db[PLAYER_KEY.format(p_steam_id) + ":pummeled:" + p]
                            msg +=  pl.name + ": ^1" + count + "^7 "
                if total:
                    self.msg("^4Pummel^7 Stats for {}: Total ^4Pummels^7: ^1{}".format(player, total))
                    if msg:
                        self.msg("^4Victims^7: {}".format(msg))
                else:
                    self.msg("{} ^7has not ^4pummeled^7 anybody on this server.".format(player))
            except Exception as e:
                minqlx.console_print("^kills exec_cmd_pummel Exception: {}".format(e))

    def cmd_airpummel(self, player, msg, channel):
        self.exec_cmd_airpummel(player, msg, channel)

    @minqlx.thread
    def exec_cmd_airpummel(self, player, msg, channel):
        if not self.kills_killMonitor[1]:
                self.msg("^4Air Pummel Kill ^7stats are not enabled on this server.")
        else:
            try:
                if len(msg) > 1:
                    player = self.player_id(msg[1], player)

                p_steam_id = player.steam_id
                total = 0
                pummels = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":airpummel")
                players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]

                msg = ""
                for p in pummels:
                    total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":airpummel:" + str(p)])
                    for pl in players:
                        if p == str(pl.steam_id):
                            count = self.db[PLAYER_KEY.format(p_steam_id) + ":airpummel:" + p]
                            msg +=  pl.name + ": ^1" + count + "^7 "
                if total:
                    self.msg("^4Air Gauntlet^7 Stats for {}: Total ^4Air Gauntlets^7: ^1{}".format(player, total))
                    if msg:
                        self.msg("^4Victims^7: {}".format(msg))
                else:
                    self.msg("{} ^7has not ^4air gauntleted^7 anybody on this server.".format(player))
            except Exception as e:
                minqlx.console_print("^kills exec_cmd_airpummel Exception: {}".format(e))

    def cmd_grenades(self, player, msg, channel):
        self.exec_cmd_grenades(player, msg, channel)

    @minqlx.thread
    def exec_cmd_grenades(self, player, msg, channel):
        if not self.kills_killMonitor[2]:
                self.msg("^4Grenade Kill ^7stats are not enabled on this server.")
        else:
            try:
                if len(msg) > 1:
                    player = self.player_id(msg[1], player)

                p_steam_id = player.steam_id
                total = 0
                grenades = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":grenaded")
                players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]

                msg = ""
                for p in grenades:
                    total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":grenaded:" + str(p)])
                    for pl in players:
                        if p == str(pl.steam_id):
                            count = self.db[PLAYER_KEY.format(p_steam_id) + ":grenaded:" + p]
                            msg += pl.name + ": ^1" + count + "^7 "
                if total:
                    self.msg("^4Grenade^7 Stats for {}: Total ^4Grenade^7 Kills: ^1{}".format(player, total))
                    if msg:
                        self.msg("^4Victims^7: {}".format(msg))
                else:
                    self.msg("{} ^7has not ^4grenade^7 killed anybody on this server.".format(player))
            except Exception as e:
                minqlx.console_print("^kills exec_cmd_grenades Exception: {}".format(e))

    def cmd_rocket(self, player, msg, channel):
        self.exec_cmd_rocket(player, msg, channel)

    @minqlx.thread
    def exec_cmd_rocket(self, player, msg, channel):
        if not self.kills_killMonitor[3]:
                self.msg("^4Air Rocket Kill ^7stats are not enabled on this server.")
        else:
            try:
                if len(msg) > 1:
                    player = self.player_id(msg[1], player)

                p_steam_id = player.steam_id
                total = 0
                rocket = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":rocket")
                players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]

                msg = ""
                for p in rocket:
                    total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":rocket:" + str(p)])
                    for pl in players:
                        if p == str(pl.steam_id):
                            count = self.db[PLAYER_KEY.format(p_steam_id) + ":rocket:" + p]
                            msg += pl.name + ": ^1" + count + "^7 "
                if total:
                    self.msg("^4Air Rocket^7 Stats for {}: Total ^4Air Rocket^7 Kills: ^1{}".format(player, total))
                    if msg:
                        self.msg("^4Victims^7: {}".format(msg))
                else:
                    self.msg("{} has not ^4air rocket^7 killed anybody on this server.".format(player))
            except Exception as e:
                minqlx.console_print("^kills exec_cmd_rocket Exception: {}".format(e))

    def cmd_plasma(self, player, msg, channel):
        self.exec_cmd_plasma(player, msg, channel)

    @minqlx.thread
    def exec_cmd_plasma(self, player, msg, channel):
        if not self.kills_killMonitor[4]:
                self.msg("^4Air Plasma Kill ^7stats are not enabled on this server.")
        else:
            try:
                if len(msg) > 1:
                    player = self.player_id(msg[1], player)

                p_steam_id = player.steam_id
                total = 0
                rocket = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":plasma")
                players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]

                msg = ""
                for p in rocket:
                    total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":plasma:" + str(p)])
                    for pl in players:
                        if p == str(pl.steam_id):
                            count = self.db[PLAYER_KEY.format(p_steam_id) + ":plasma:" + p]
                            msg += pl.name + ": ^1" + count + "^7 "
                if total:
                    self.msg("^4Air Plasma^7 Stats for {}: Total ^4Air Plasma^7 Kills: ^1{}".format(player, total))
                    if msg:
                        self.msg("^4Victims^7: {}".format(msg))
                else:
                    self.msg("{} has not ^4air plasma^7 killed anybody on this server.".format(player))
            except Exception as e:
                minqlx.console_print("^kills exec_cmd_plasma Exception: {}".format(e))

    def cmd_airrail(self, player, msg, channel):
        self.exec_cmd_airrail(player, msg, channel)

    @minqlx.thread
    def exec_cmd_airrail(self, player, msg, channel):
        if not self.kills_killMonitor[5]:
                self.msg("^4Air Rail Kill ^7stats are not enabled on this server.")
        else:
            try:
                if len(msg) > 1:
                    player = self.player_id(msg[1], player)

                p_steam_id = player.steam_id
                total = 0
                pummels = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":airrail")
                players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]

                msg = ""
                for p in pummels:
                    total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":airrail:" + str(p)])
                    for pl in players:
                        if p == str(pl.steam_id):
                            count = self.db[PLAYER_KEY.format(p_steam_id) + ":airrail:" + p]
                            msg +=  pl.name + ": ^1" + count + "^7 "
                if total:
                    self.msg("^4Air Rail^7 Stats for {}: Total ^4Air Rails^7: ^1{}".format(player, total))
                    if msg:
                        self.msg("^4Victims^7: {}".format(msg))
                else:
                    self.msg("{} ^7has not ^4air railed^7 anybody on this server.".format(player))
            except Exception as e:
                minqlx.console_print("^kills exec_cmd_airrail Exception: {}".format(e))

    def cmd_telefrag(self, player, msg, channel):
        self.exec_cmd_telefrag(player, msg, channel)

    @minqlx.thread
    def exec_cmd_telefrag(self, player, msg, channel):
        if not self.kills_killMonitor[6]:
                self.msg("^4Telefrag Kill ^7stats are not enabled on this server.")
        else:
            try:
                if len(msg) > 1:
                    player = self.player_id(msg[1], player)

                p_steam_id = player.steam_id
                total = 0
                rocket = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":telefrag")
                players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]

                msg = ""
                for p in rocket:
                    total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":telefrag:" + str(p)])
                    for pl in players:
                        if p == str(pl.steam_id):
                            count = self.db[PLAYER_KEY.format(p_steam_id) + ":telefrag:" + p]
                            msg += pl.name + ": ^1" + count + "^7 "
                if total:
                    self.msg("^4Telefrag^7 Stats for {}: Total ^4Telefrag^7 Kills: ^1{}".format(player, total))
                    if msg:
                        self.msg("^4Victims^7: {}".format(msg))
                else:
                    self.msg("{} has not ^4telefrag^7 killed anybody on this server.".format(player))
            except Exception as e:
                minqlx.console_print("^kills exec_cmd_telefrag Exception: {}".format(e))

    def cmd_teamtelefrag(self, player, msg, channel):
        self.exec_cmd_teamtelefrag(player, msg, channel)

    @minqlx.thread
    def exec_cmd_teamtelefrag(self, player, msg, channel):
        if not self.kills_killMonitor[7]:
                self.msg("^4Team Telefrag Kill ^7stats are not enabled on this server.")
        else:
            try:
                if len(msg) > 1:
                    player = self.player_id(msg[1], player)

                p_steam_id = player.steam_id
                total = 0
                rocket = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":teamtelefrag")
                players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]

                msg = ""
                for p in rocket:
                    total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":teamtelefrag:" + str(p)])
                    for pl in players:
                        if p == str(pl.steam_id):
                            count = self.db[PLAYER_KEY.format(p_steam_id) + ":teamtelefrag:" + p]
                            msg += pl.name + ": ^1" + count + "^7 "
                if total:
                    self.msg("^4Team Telefrag^7 Stats for {}: Total ^4Team Telefrag^7 Kills: ^1{}".format(player, total))
                    if msg:
                        self.msg("^4Victims^7: {}".format(msg))
                else:
                    self.msg("{} has not ^4team telefrag^7 killed anybody on this server.".format(player))
            except Exception as e:
                minqlx.console_print("^kills exec_cmd_teamtelefrag Exception: {}".format(e))

    def cmd_speedkill(self, player, msg, channel):
        self.exec_cmd_speedkill(player, msg, channel)

    @minqlx.thread
    def exec_cmd_speedkill(self, player, msg, channel):
        if not self.kills_killMonitor[8]:
                self.msg("^4Speed Kill ^7stats are not enabled on this server.")
        else:
            try:
                if len(msg) > 1:
                    player = self.player_id(msg[1], player)

                p_steam_id = player.steam_id
                total = 0
                rocket = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":speedkill")
                players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]

                msg = ""
                for p in rocket:
                    total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":speedkill:" + str(p)])
                    for pl in players:
                        if p == str(pl.steam_id):
                            count = self.db[PLAYER_KEY.format(p_steam_id) + ":speedkill:" + p]
                            msg += pl.name + ": ^1" + count + "^7 "
                if total:
                    self.msg("^4Speed Kill^7 Stats for {}: Total ^4Speed^7 Kills: ^1{}".format(player, total))
                    self.msg("^4Highest Kill Speed^7: ^3{}"
                             .format(self.db[PLAYER_KEY.format(player.steam_id) + ":highspeed"].split(".")[0]))
                    if msg:
                        self.msg("^4Victims^7: {}".format(msg))
                else:
                    self.msg("{} has not ^4speed^7 killed anybody on this server.".format(player))
            except Exception as e:
                minqlx.console_print("^kills exec_cmd_speedkill Exception: {}".format(e))

    def add_killer(self, killer, method):
        try:
            if method == "GAUNTLET":
                try:
                    self.kills_pummel[killer] += 1
                except:
                    self.kills_pummel[killer] = 1
            elif method == "AIRGAUNTLET":
                try:
                    self.kills_airpummel[killer] += 1
                except:
                    self.kills_airpummel[killer] = 1
            elif method == "GRENADE":
                try:
                    self.kills_grenades[killer] += 1
                except:
                    self.kills_grenades[killer] = 1
            elif method == "ROCKET":
                try:
                    self.kills_rockets[killer] += 1
                except:
                    self.kills_rockets[killer] = 1
            elif method == "PLASMA":
                try:
                    self.kills_plasma[killer] += 1
                except:
                    self.kills_plasma[killer] = 1
            elif method == "AIRRAIL":
                try:
                    self.kills_airrail[killer] += 1
                except:
                    self.kills_airrail[killer] = 1
            elif method == "TELEFRAG":
                try:
                    self.kills_telefrag[killer] += 1
                except:
                    self.kills_telefrag[killer] = 1
            elif method == "TEAMTELEFRAG":
                try:
                    self.kills_teamtelefrag[killer] += 1
                except:
                    self.kills_teamtelefrag[killer] = 1
            elif method == "SPEED":
                try:
                    self.kills_speed[killer] += 1
                except:
                    self.kills_speed[killer] = 1
        except Exception as e:
            minqlx.console_print("^kills add_killer Exception: {}".format(e))

    def sound_play(self, path):
        try:
            for p in self.players():
                if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                    super().play_sound(path, p)
        except Exception as e:
            minqlx.console_print("^kills sound_play Exception: {}".format(e))

    def supported_games(self, player, msg, channel):
        self.msg("^4Special kills ^7are recorded on this server when playing gateypes:")
        self.msg("^3{}".format(str(SUPPORTED_GAMETYPES)))

    def kills_recorded(self, player, msg, channel):
        self.msg("^4Special kills ^7may be recorded when these kills are made:")
        self.msg("^3Pummel^7, ^3Air Gauntlet^7, ^3Direct Grenade^7, ^3Mid-Air Rocket^7,\n"
                 "^3Mid-Air Plasma^7, ^3Air Rails^7, ^3Telefrags^7, ^3Team Telefrags^7,\n"
                 " and ^3Speed Kills")
        self.msg("^6Commands^7: ^4!pummel^7, ^4!airgauntlet^7, ^4!grenades^7, ^4!rockets^7,\n"
                " ^4!plasma^7, ^4!airrails^7, ^4!telefrag^7, ^4!teamtelefrag^7, ^4!speed^7,\n"
                 " ^4!speedlimit")

    def player_id(self, pid, player):
        try:
            pid = int(pid)
            if 0 <= pid <= 63:
                try:
                    target_player = self.player(pid)
                except minqlx.NonexistentPlayerError:
                    player.tell("^3Invalid client ID. Use a client ID.")
                    return minqlx.RET_STOP_EVENT
                if not target_player:
                    player.tell("^3Invalid client ID. Use a client ID.")
                    return minqlx.RET_STOP_EVENT
            elif pid < 0:
                player.tell("^3usage^7=^7<^2player id^7>")
                return minqlx.RET_STOP_EVENT
            elif len(str(pid)) != 17:
                player.tell("^3STEAM ID's are not supported.")
                return minqlx.RET_STOP_EVENT
        except ValueError:
            player.tell("^3Invalid ID. Use a client ID.")
            return minqlx.RET_STOP_EVENT
        except Exception as e:
            minqlx.console_print("^kills player_id Exception: {}".format(e))

        return target_player

    def cmd_kills_monitor(self, player=None, msg=None, channel=None):
        try:
            games = self.get_cvar("qlx_killsMonitorKillTypes", int)
            binary = bin(games)[2:]
            length = len(str(binary))
            count = 0

            while length > 0:
                self.kills_killMonitor[count] = int(binary[length - 1])
                count += 1
                length -= 1

            if player:
                player.tell("Monitor: {}".format(str(self.kills_killMonitor)))
                return minqlx.RET_STOP_ALL
        except Exception as e:
            minqlx.console_print("^kills cmd_kills_monitor Exception: {}".format(e))

    def kills_version(self, player, msg, channel):
        self.msg("^7This server is running ^4Kills^7 Version^1 1.16")
