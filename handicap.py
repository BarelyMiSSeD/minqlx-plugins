"""
This is an extension plugin  for minqlx, a Quake Live Server Admin Tool..
Copyright (C) 2016 BarelyMiSSeD (github)

You can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

You should have received a copy of the GNU General Public License
along with minqlx. If not, see <http://www.gnu.org/licenses/>.

Handicap.py is a simple script made to automatically put a handicap on people who are over a certain ELO.
It will calculate the percentage of a handicap to put on a player based on the lower and upper ELO settings.
"""

import minqlx
import requests

"""
The handicap given to players above the LOWER_ELO setting.
The severity of the handicap given can be adjusted by changing the UPPER_ELO setting.
Increase it to reduce the severity of the handicap and lower it to increase the severity.
It should not be lowered further than the highest ELO connected to the server.
****Adjust the LOWER_ELO to the level you want the script to start giving handicaps***
****Adjust the UPPER_ELO to adjust the amount of handicap it gives. The higher the UPPER_ELO***
****the less severe the handicap.***
"""
UPPER_ELO = 3500
LOWER_ELO = 1800


MAX_ATTEMPTS = 3
ELO_KEY = "minqlx:players:{}:elo:{}:{}"
VERSION = 1.10


class handicap(minqlx.Plugin):
    def __init__(self):
        self.set_cvar_once("qlx_handicapAdminLevel", "3")
        self.set_cvar_once("qlx_handicapMsgPlayer", "1")

        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("userinfo", self.handle_user_info)
        self.add_command(("handicap", "handi"), self.cmd_handicap, self.get_cvar("qlx_handicapAdminLevel", int))
        self.add_command("hversion", self.cmd_hversion)
        self.add_command(("handicapon", "handion"), self.cmd_handicap_on,
                         self.get_cvar("qlx_handicapAdminLevel", int))
        self.add_command(("handicapoff", "handioff"), self.cmd_handicap_off,
                         self.get_cvar("qlx_handicapAdminLevel", int))
        self.add_command(("listhandicaps", "listhandi"), self.cmd_list_handicaps,
                         self.get_cvar("qlx_handicapAdminLevel", int))

        self.handicapped_players = {}
        self.handicap_gametype = self.game.type_short
        self.temp_on = True

        self.check_players()

    @minqlx.thread
    def check_players(self):
        if self.temp_on:
            players = self.players()
            pids = ""
            gtype = self.handicap_gametype
            elo = self.get_cvar("qlx_balanceApi")
            response = False

            for player in players:
                pids += "{}+".format(player.steam_id)
            pids = pids[:-1]

            url = "http://{}/{}/{}".format(self.get_cvar("qlx_balanceUrl"), elo, pids)
            attempts = 0
            while attempts < MAX_ATTEMPTS:
                attempts += 1
                info = requests.get(url)
                if info.status_code != requests.codes.ok:
                    continue
                info_js = info.json()
                if "players" in info_js:
                    attempts = MAX_ATTEMPTS
                    response = True
            if response:
                for info in info_js["players"]:
                    rating = int(info[str(gtype)]["elo"])
                    if rating > LOWER_ELO:
                        percentage = 100 - abs(round(((LOWER_ELO - rating) / (UPPER_ELO - LOWER_ELO)) * 100))
                        self.handicapped_players[str(info["steamid"])] = percentage
            else:
                for player in players:
                    rating = 0
                    pid = player.steam_id
                    try:
                        rating = int(self.db.get(ELO_KEY.format(pid, elo, gtype)))
                    except:
                        pass
                    if rating > LOWER_ELO:
                        percentage = 100 - abs(round(((LOWER_ELO - rating) / (UPPER_ELO - LOWER_ELO)) * 100))
                        self.handicapped_players[str(pid)] = percentage

            for player in players:
                pid = player.steam_id
                if self.handicapped_players[str(pid)]:
                    player.handicap = int(self.handicapped_players[str(pid)])

    def cmd_handicap_on(self, player, msg, channel):
        self.temp_on = True
        player.tell("^3Players will now not be able to change their handicaps")
        self.check_players()
        return minqlx.RET_STOP_ALL

    def cmd_handicap_off(self, player, msg, channel):
        self.temp_on = False
        player.tell("^3Players will now be able to change their handicaps")
        return minqlx.RET_STOP_ALL

    def cmd_handicap(self, player, msg, channel):
        if len(msg) < 3:
            player.msg("^3Usage: <player ID> <handicap>")
            return minqlx.RET_STOP_ALL

        try:
            pid = int(msg[1])
            handi = int(msg[2])
        except ValueError:
            player.tell("^1Use a valid Player ID and a handicap between 1 and 100.")
            return minqlx.RET_STOP_ALL

        target_player = self.player(pid)

        if handi <= 0 or handi > 100:
            player.tell("^3The handicap must be between 1 and 100.")
            return minqlx.RET_STOP_ALL

        if target_player:
            self.handicapped_players[str(target_player.steam_id)] = handi
            target_player.handicap = handi
            if int(self.get_cvar("qlx_handicapMsgPlayer")):
                self.message_player(target_player, handi)
        return minqlx.RET_STOP_ALL

    def cmd_list_handicaps(self, player, msg, channel):
        if len(self.handicapped_players):
            handi_list = ""
            players = self.players()
            for pl, handi in self.handicapped_players.items():
                for p in players:
                    if p.steam_id == int(pl):
                        plyer = p
                handi_list += "^7{} ^7: ^2{}％\n".format(plyer, handi)
            player.tell(handi_list)
        else:
            player.tell("^3There is no one being hadnicapped on the server by the {} script."
                        .format(self.__class__.__name__))
        return minqlx.RET_STOP_ALL


    def handle_player_loaded(self, player):
        if self.temp_on:
            gtype = self.handicap_gametype
            elo = self.get_cvar("qlx_balanceApi")
            response = False
            pid = player.steam_id
            url = "http://{}/{}/{}".format(self.get_cvar("qlx_balanceUrl"), elo, pid)
            attempts = 0
            while attempts < MAX_ATTEMPTS:
                attempts += 1
                info = requests.get(url)
                if info.status_code != requests.codes.ok:
                    continue
                info_js = info.json()
                if "players" in info_js:
                    attempts = MAX_ATTEMPTS
                    response = True
            if response:
                for info in info_js["players"]:
                    rating = int(info[str(gtype)]["elo"])
                    if rating > LOWER_ELO:
                        percentage = 100 - abs(round(((LOWER_ELO - rating) / (UPPER_ELO - LOWER_ELO)) * 100))
                        self.handicapped_players[str(pid)] = percentage
                        player.handicap = abs(int(self.handicapped_players[str(pid)]))
                        if int(self.get_cvar("qlx_handicapMsgPlayer")):
                            self.message_player(player, percentage)

    def message_player(self, player, percentage):
        player.tell("^7You, {}^7 have been set to an auto handicap of ^1{}％ ^7because your elo is over ^4{}^7."
                    .format(player, percentage, LOWER_ELO))

    def cmd_hversion(self, player, msg, channel):
        channel.reply('^7This server has installed ^2{} version {} by BarelyMiSSeD'
                      .format(self.__class__.__name__, VERSION))

    def handle_user_info(self, player, info):
        if "handicap" in info:
            if self.handicapped_players[str(player.steam_id)] and self.temp_on:
                player.tell("^1Your handicap is being set by the server and can't be changed.")
                info['handicap'] = self.handicapped_players[str(player.steam_id)]
            return info

    @minqlx.delay(5)
    def handle_new_game(self):
        gtype = self.game.type_short
        if gtype != self.handicap_gametype and self.temp_on:
            self.handicap_gametype = gtype
            self.check_players()

    def handle_player_disconnect(self, player, reason):
        pid = player.steam_id
        if self.handicapped_players[str(pid)]:
            del self.handicapped_players[str(pid)]
