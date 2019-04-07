# permsText.py is a plugin for minqlx to:
# This will save permissions on the server to a text file so the file can be moved to another
#  server and loaded onto that database.
# It will also list the players who have permissions on the server
# created by BarelyMiSSeD on 11-10-15
#
"""
!getperms - This will get the permissions on the server and store it in the PERMS_FILE in the fs_homepath directory
!addperms - This will read the PERMS_FILE in the fs_homepath directory and put those perms into the database
!listperms - This will list the players with permissions on the server
"""

import minqlx
import os

PLAYER_KEY = "minqlx:players:{}:permission"
PERMS_FILE = "server_perms.txt"


class permsText(minqlx.Plugin):
    def __init__(self):
        self.add_command("getperms", self.get_perms, 5)
        self.add_command("addperms", self.add_perms, 5)
        self.add_command("listperms", self.list_perms, 5)

    def get_perms(self, player, msg, channel):
        self.save_perms()

    @minqlx.thread
    def save_perms(self):
        playerlist = self.db.keys(PLAYER_KEY.format("*"))
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
            self.db.set(PLAYER_KEY.format(info[0]), int(info[1]))
        minqlx.console_print("^1Finished entering player permissions to the database.")
        h.close()

        return minqlx.RET_STOP_ALL

    def list_perms(self, player, msg, channel):
        self.show_perms(player)

    @minqlx.thread
    def show_perms(self, asker):
        minqlx.console_print("{}".format(str([asker])))
        playerlist = self.db.keys(PLAYER_KEY.format("*"))
        perms_list0 = []
        perms_list1 = []
        perms_list2 = []
        perms_list3 = []
        perms_list4 = []
        perms_list5 = []
        for player in playerlist:
            steam_id = player.split(":")[2]
            if len(str(steam_id)) == 17:
                perms = int(self.db.get(player))
                if perms == 0:
                    perms_list0.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex("minqlx:players:{}".format(steam_id), 0),
                                               steam_id, perms, perms))
                elif perms == 1:
                    perms_list1.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex("minqlx:players:{}".format(steam_id), 0),
                                               steam_id, perms, perms))
                elif perms == 2:
                    perms_list2.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex("minqlx:players:{}".format(steam_id), 0),
                                               steam_id, perms, perms))
                elif perms == 3:
                    perms_list3.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex("minqlx:players:{}".format(steam_id), 0),
                                               steam_id, perms, perms))
                elif perms == 4:
                    perms_list4.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex("minqlx:players:{}".format(steam_id), 0),
                                               steam_id, perms, perms))
                elif perms == 5:
                    perms_list5.append("{} ^7({}): ^{}{}"
                                       .format(self.db.lindex("minqlx:players:{}".format(steam_id), 0),
                                               steam_id, perms, perms))
        owner = minqlx.owner()
        asker.tell("^1Server Owner^7: {} ^7({})".format(self.db.lindex("minqlx:players:{}".format(owner), 0), owner))
        if len(perms_list5) > 0:
            asker.tell("^5Level 5 Permissions^7:\n" + "\n^7".join(perms_list5))
        if len(perms_list4) > 0:
            asker.tell("^4Level 4 Permissions^7:\n" + "\n^7".join(perms_list4))
        if len(perms_list3) > 0:
            asker.tell("^3Level 3 Permissions^7:\n" + "\n^7".join(perms_list3))
        if len(perms_list2) > 0:
            asker.tell("^2Level 2 Permissions^7:\n" + "\n^7".join(perms_list2))
        if len(perms_list1) > 0:
            asker.tell("^1Level 1 Permissions^7:\n" + "\n^7".join(perms_list1))
        if len(perms_list0) > 0:
            asker.tell("^0Level 0 Permissions^7:\n" + "\n^7".join(perms_list0))

        return minqlx.RET_STOP_ALL


