# players_db.py is a plugin for minqlx to:
# This will save permissions on the server to a text file so the file can be moved to another
#  server and loaded onto that database.
# It will also list the players who have permissions on the server, banned players, and silenced players
# created by BarelyMiSSeD on 11-10-15
#
"""
!getperms - This will get the permissions on the server and store it in the PERMS_FILE in the fs_homepath directory
!addperms - This will read the PERMS_FILE in the fs_homepath directory and put those perms into the database
!perms - This will list the players with permissions on the server
!bans - This will list the banned players on the server
!silenced - This will list the silenced players on the server
"""

import minqlx
import os
import time
import datetime

PLAYER_KEY = "minqlx:players:{}"
PLAYER_DB_KEY = "minqlx:players:{}:{}"
PERMS_FILE = "server_perms.txt"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class players_db(minqlx.Plugin):
    def __init__(self):
        self.add_command("getperms", self.get_perms, 5)
        self.add_command("addperms", self.add_perms, 5)
        self.add_command(("perms", "listperms"), self.list_perms, 4)
        self.add_command(("bans", "banned", "listbans"), self.list_bans, 4)
        self.add_command(("silenced", "silences", "listsilenced"), self.list_silenced, 4)
        self.add_command("leavers", self.list_leavers, 4)
        self.add_command("warned", self.list_warned, 4)

    def get_perms(self, player, msg, channel):
        self.save_perms()
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def save_perms(self):
        playerlist = self.db.keys(PLAYER_DB_KEY.format("*", "permission"))
        file = os.path.join(self.get_cvar("fs_homepath"), PERMS_FILE)
        try:
            h = open(file, "w")
        except Exception as e:
            minqlx.console_print("^1ERROR Opening perms file: {}".format(e))
            return minqlx.RET_STOP_ALL
        for player in playerlist:
            steam_id = player.split(":")[2]
            if len(str(steam_id)) == 17:
                h.write("{}:{}".format(steam_id, self.db.get(player)) + "\n")
        minqlx.console_print("^1Finished saving player permissions to {}".format(PERMS_FILE))
        h.close()

        return minqlx.RET_STOP_ALL

    def add_perms(self, player, msg, channel):
        self.enter_perms()
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def enter_perms(self):
        file = os.path.join(self.get_cvar("fs_homepath"), PERMS_FILE)
        try:
            h = open(file, "r")
        except Exception as e:
            minqlx.console_print("^1ERROR Opening perms file: {}".format(e))
            return minqlx.RET_STOP_ALL
        for player in h.readlines():
            info = player.split(":")
            self.db.set(PLAYER_DB_KEY.format(info[0], "permission"), int(info[1]))
        minqlx.console_print("^1Finished entering player permissions to the database.")
        h.close()

        return minqlx.RET_STOP_ALL

    def list_perms(self, player, msg, channel):
        self.show_perms(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_perms(self, asker):
        playerlist = self.db.keys(PLAYER_DB_KEY.format("*", "permission"))
        perms_list1 = []
        perms_list2 = []
        perms_list3 = []
        perms_list4 = []
        perms_list5 = []
        for player in playerlist:
            steam_id = player.split(":")[2]
            if len(str(steam_id)) == 17:
                perms = int(self.db.get(player))
                if perms == 1:
                    perms_list1.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex(PLAYER_KEY.format(steam_id), 0),
                                               steam_id, perms, perms))
                elif perms == 2:
                    perms_list2.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex(PLAYER_KEY.format(steam_id), 0),
                                               steam_id, perms, perms))
                elif perms == 3:
                    perms_list3.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex(PLAYER_KEY.format(steam_id), 0),
                                               steam_id, perms, perms))
                elif perms == 4:
                    perms_list4.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex(PLAYER_KEY.format(steam_id), 0),
                                               steam_id, perms, perms))
                elif perms == 5:
                    perms_list5.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex(PLAYER_KEY.format(steam_id), 0),
                                               steam_id, perms, perms))
        owner = minqlx.owner()
        asker.tell("^1Server Owner^7: {} ^7({})".format(self.db.lindex(PLAYER_KEY.format(owner), 0), owner))
        if len(perms_list5) > 0:
            asker.tell("^5Level 5 Permissions^7:")
            for p in perms_list5:
                asker.tell(p)
        if len(perms_list4) > 0:
            asker.tell("^4Level 4 Permissions^7:")
            for p in perms_list4:
                asker.tell(p)
        if len(perms_list3) > 0:
            asker.tell("^3Level 3 Permissions^7:")
            for p in perms_list3:
                asker.tell(p)
        if len(perms_list2) > 0:
            asker.tell("^2Level 2 Permissions^7:")
            for p in perms_list2:
                asker.tell(p)
        if len(perms_list1) > 0:
            asker.tell("^1Level 1 Permissions^7:")
            for p in perms_list1:
                asker.tell(p)

        return

    def list_bans(self, player, msg, channel):
        self.show_bans(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_bans(self, asker):
        playerlist = self.db.keys(PLAYER_DB_KEY.format("*", "bans"))
        bans_list = []
        for player in playerlist:
            steam_id = player.split(":")[2]
            banned = self.db.zrangebyscore(PLAYER_DB_KEY.format(steam_id, "bans"), time.time(), "+inf", withscores=True)
            if banned:
                longest_ban = self.db.hgetall(PLAYER_DB_KEY.format(steam_id, "bans") + ":{}".format(banned[-1][0]))
                expires = datetime.datetime.strptime(longest_ban["expires"], TIME_FORMAT)
                if (expires - datetime.datetime.now()).total_seconds() > 0:
                    bans_list.append("{} ^7({}): ^6Expires: ^7{} ^5Reason: ^7{} ^2Issued By: ^7{}"
                                     .format(self.db.lindex(PLAYER_KEY.format(steam_id), 0),
                                             steam_id, datetime.datetime.strptime(longest_ban["expires"],
                                                                                  TIME_FORMAT),
                                             longest_ban["reason"] if longest_ban["reason"] else "No Saved Reason",
                                             self.db.lindex(PLAYER_KEY.format(longest_ban["issued_by"]), 0)))
        if len(bans_list) > 0:
            asker.tell("^5Bans^7:")
            for ban in bans_list:
                asker.tell(ban)
        else:
            asker.tell("^5No Active bans found.")

        return

    def list_silenced(self, player, msg, channel):
        self.show_silenced(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_silenced(self, asker):
        playerlist = self.db.keys(PLAYER_DB_KEY.format("*", "silences"))
        message = []
        for player in playerlist:
            steam_id = player.split(":")[2]
            silenced = self.db.zrangebyscore(PLAYER_DB_KEY.format(steam_id, "silences"), time.time(), "+inf",
                                             withscores=True)
            if silenced:
                silence_time = self.db.hgetall(PLAYER_DB_KEY.format(steam_id, "silences") + ":{}"
                                               .format(silenced[-1][0]))
                expires = datetime.datetime.strptime(silence_time["expires"], TIME_FORMAT)
                if (expires - datetime.datetime.now()).total_seconds() > 0:
                    message.append("{} ^7({}): ^6Expires: ^7{} ^5Reason: ^7{} ^2Issued By: ^7{}"
                                   .format(self.db.lindex(PLAYER_KEY.format(steam_id), 0),
                                           steam_id, datetime.datetime.strptime(silence_time["expires"],
                                                                                TIME_FORMAT),
                                           silence_time["reason"] if silence_time["reason"] else "No Saved Reason",
                                           self.db.lindex(PLAYER_KEY.format(silence_time["issued_by"]), 0)))
        if len(message) > 0:
            asker.tell("^5Silenced^7:")
            for silence in message:
                asker.tell(silence)
        else:
            asker.tell("^5No Active silences found.")

        return

    def list_leavers(self, player, msg, channel):
        self.show_leavers(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_leavers(self, asker):
        if not self.get_cvar("qlx_leaverBan", bool):
            asker.tell("^5Leaver bans are not enabled on this server.")
        else:
            playerlist = self.db.keys(PLAYER_KEY.format("*"))
            message = []
            for player in playerlist:
                steam_id = player.split(":")[2]
                try:
                    completed = self.db[PLAYER_KEY.format(steam_id) + ":games_completed"]
                    left = self.db[PLAYER_KEY.format(steam_id) + ":games_left"]
                except KeyError:
                    continue
                completed = int(completed)
                left = int(left)
                min_games_completed = self.get_cvar("qlx_leaverBanMinimumGames", int)
                ban_threshold = self.get_cvar("qlx_leaverBanThreshold", float)
                total = completed + left
                if not total:
                    continue
                elif total < min_games_completed:
                    continue
                else:
                    ratio = completed / total
                if ratio <= ban_threshold and total >= min_games_completed:
                    message.append("{} ^7({}): ^6Games Played: ^7{} ^5Left: ^7{} ^4Percent: ^7{}"
                                   .format(self.db.lindex(PLAYER_KEY.format(steam_id), 0),
                                           steam_id, total, left, ratio))

            if len(message) > 0:
                asker.tell("^5Leaver Banned^7:")
                for leaver in message:
                    asker.tell(leaver)
            else:
                asker.tell("^5No Leaver Bans found.")
        return

    def list_warned(self, player, msg, channel):
        self.show_warned(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_warned(self, asker):
        if not self.get_cvar("qlx_leaverBan", bool):
            asker.tell("^5Leaver bans are not enabled on this server.")
        else:
            playerlist = self.db.keys(PLAYER_KEY.format("*"))
            message = []
            for player in playerlist:
                steam_id = player.split(":")[2]
                try:
                    completed = self.db[PLAYER_KEY.format(steam_id) + ":games_completed"]
                    left = self.db[PLAYER_KEY.format(steam_id) + ":games_left"]
                except KeyError:
                    continue
                completed = int(completed)
                left = int(left)
                min_games_completed = self.get_cvar("qlx_leaverBanMinimumGames", int)
                warn_threshold = self.get_cvar("qlx_leaverBanWarnThreshold", float)
                ban_threshold = self.get_cvar("qlx_leaverBanThreshold", float)
                total = completed + left
                if not total:
                    continue
                elif total < min_games_completed:
                    continue
                else:
                    ratio = completed / total
                if ratio <= warn_threshold and (ratio > ban_threshold or total < min_games_completed):
                    message.append("{} ^7({}): ^6Games Played: ^7{} ^5Left: ^7{} ^4Percent: ^7{}"
                                   .format(self.db.lindex(PLAYER_KEY.format(steam_id), 0),
                                           steam_id, total, left, ratio))

            if len(message) > 0:
                asker.tell("^5Leaver Warned^7:")
                for leaver in message:
                    asker.tell(leaver)
            else:
                asker.tell("^5No Leaver Warned found.")
        return
