# voteban.py is a plugin for minqlx to:
# -add people to a vote ban list that would keep them from being able to vote on the server at all.
# -the vote ban can be added with a time duration or be made permamnent.
# -the vote ban may be removed or extended.
# created by BarelyMiSSeD on 2-22-16
# 
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
qlx_votebanAdmin "5" - Sets the permisson level needed to add and remove someones server voting privilage.
                    Voting privilage can only be removed from players below the qlx_votebanProtectionLevel setting.
qlx_votebanProtectionLevel "5" - If the person being added to the vote ban list has this minqlx server permission level,
                    they can't be added to the vote ban list.
qlx_votebanVoteBan "1" - Toruns on/off vote banning. Vote banning will remove voting privilages from a player on the server.
"""

import minqlx
import re
import threading
import requests
import datetime
import time

LENGTH_REGEX = re.compile(r"(?P<number>[0-9]+) (?P<scale>seconds?|minutes?|hours?|days?|weeks?|months?|years?)")
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

VERSION = "v1.00"

class voteban(minqlx.Plugin):
    def __init__(self):
        self.add_hook("player_loaded", self.player_loaded)
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)

        # Cvars.
        self.set_cvar_once("qlx_votebanAdmin", "5")
        self.set_cvar_once("qlx_votebanProtectionLevel", "5")
        self.set_cvar_once("qlx_votebanVoteBan", "1")

        # Commands: permission level is set using some of the Cvars. See the Cvars descrition at the top of the file.
        self.add_command(("voteban", "vote_ban", "banvote", "ban_vote"), self.cmd_voteBan, int(self.get_cvar("qlx_votebanAdmin")))
        self.add_command(("voteunban", "vote_unban", "unbanvote", "unban_vote"), self.cmd_voteUnBan, int(self.get_cvar("qlx_votebanAdmin")))
        self.add_command(("v_voteban", "version_voteban", "votebanversion", "voteban_version", "voteban_v"), self.voteban_version, int(self.get_cvar("qlx_votebanAdmin")))
        self.add_command(("listvoteban", "list_voteban", "votebanlist", "voteban_list"), self.cmd_voteBanList, int(self.get_cvar("qlx_votebanAdmin")))
        self.add_command("vblist", self.cmd_VBList, 5) # command for testing purposes

        # Checks for a voteban.txt file and loads the entries if the file exists.
        try:
            list = open(self.get_cvar("fs_homepath") + "/voteban.txt").readlines()
            self.voteban = []
            for id in list:
                if id.startswith("#"): continue
                words = id.split(" ")
                steamID = words[0]
                timeEnd = " ".join(words[3:5])
                banEnd = datetime.datetime.strptime(timeEnd, TIME_FORMAT)
                if (banEnd - datetime.datetime.now()).total_seconds() > 0:
                    self.voteban.append(int(steamID))
        except:
            self.voteban = []

    # voteban.py version checker. Thanks to iouonegirl for most of this section's code.
    @minqlx.thread
    def check_version(self, player=None, channel=None):
        url = "https://raw.githubusercontent.com/barelymissed/minqlx-plugins/master/{}.py".format(self.__class__.__name__)
        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                # If called manually and outdated
                if channel and VERSION.encode() != line:
                    channel.reply("^4Server: ^7Currently using  ^4BarelyMiSSeD^7's ^6{}^7 plugin ^1outdated^7 version ^6{}^7. The latest version is ^6{}".format(self.__class__.__name__, VERSION, line.decode()))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If called manually and alright
                elif channel and VERSION.encode() == line:
                    channel.reply("^4Server: ^7Currently using ^4BarelyMiSSeD^7's  latest ^6{}^7 plugin version ^6{}^7.".format(self.__class__.__name__, VERSION))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If routine check and it's not alright.
                elif player and VERSION.encode() != line:
                    try:
                        player.tell("^4Server: ^3Plugin update alert^7:^6 {}^7's latest version is ^6{}^7 and you're using ^6{}^7!".format(self.__class__.__name__, line.decode(), VERSION))
                        player.tell("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                    except Exception as e: minqlx.console_command("echo {}".format(e))
                return

    def voteban_version(self, player, msg, channel):
        self.check_version(channel=channel)

    # Checks the vote ban list when a player connects to see if vote ban time has passed.
    def player_loaded(self, player):
        id = int(player.steam_id)
        if id in self.voteban:
            f = open(self.get_cvar("fs_homepath") + "/voteban.txt")
            list = f.readlines()
            f.close()
            for searchID in list:
                if searchID.startswith("#"): continue
                if id == int(searchID.split(None, 1)[0]):
                    words = searchID.split(" ")
                    timeEnd = " ".join(words[3:5])
                    banEnd = datetime.datetime.strptime(timeEnd, TIME_FORMAT)
                    if (banEnd - datetime.datetime.now()).total_seconds() <= 0:
                        self.voteban.remove(id)

    # Handles votes called: Stops votes called by clients in the vote ban list.
    def handle_vote_called(self, caller, vote, args):
        id = int(caller.steam_id)
        if id in self.voteban:
            caller.tell("^3You are not permitted to callvote anything on this server.")
            return minqlx.RET_STOP_ALL

    # Command for testing: shows the contents of the self.protect string used to protect players from being kicked.
    def cmd_VBList(self, player, msg, channel):
        player.tell("List: " + str(self.voteban))

    # Adds the desired player to the vote ban file to ban callvoting anything on the server for the set time period.
    def cmd_voteBan(self, player, msg, channel):
        if len(msg) < 4:
            player.tell("^3usage^7=^7<^2player id^7|^2steam id^7> <^2number^7>[0-9] "
                        "^7<^2scale^7>seconds?|minutes?|hours?|days?|weeks?|months?|years? |^2name^7 if using steam_id|")
            return minqlx.RET_STOP_EVENT

        file = self.get_cvar("fs_homepath") + "/voteban.txt"
        try:
            with open(file) as test:
                pass
        except:
            m = open(file, "w")
            m.write("# This is a commented line because it starts with a '#'\n")
            m.write("# Enter every vote ban on a newline, format: SteamID Issued Time EndBan Time Name\n")
            m.write("# The NAME is for a mental reference and may contain spaces.\n")
            m.write("# NAME will be added automatically if the ban is added with a client id when the player is connected to the server.\n")
            m.close()

        target_player = False

        # Checks to see if client_id or steam_id was used
        try:
            id = int(msg[1])
            if 0 <= id <= 63:
                target_player = self.player(id)
                if not target_player:
                    player.tell("^3There is no one on the server using that Client ID.")
                    return minqlx.RET_STOP_EVENT
                id = int(target_player.steam_id)
        except ValueError:
            player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
            return minqlx.RET_STOP_EVENT
        except minqlx.NonexistentPlayerError:
            player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
            return minqlx.RET_STOP_EVENT
        if len(str(id)) != 17:
            player.tell("^3The STEAM ID given needs to be 17 digits in length.")
            return minqlx.RET_STOP_EVENT

        if target_player:
            messageName = target_player
        else:
            messageName = str(id)
            if len(msg) > 3:
                target_player = msg[4:]
            else:
                target_player = "Name not supplied"

        # Checks player permission level and will not vote ban players with at least the qlx_protectPermissionLevel setting.
        if self.db.has_permission(id, int(self.get_cvar("qlx_votebanProtectionLevel"))):
            player.tell("^2{} ^3is not allowed to be vote banned. Protected permission level or higher has been assigned.".format(messageName))
            return minqlx.RET_STOP_EVENT

        # Calculates the length of the Vote Ban
        r = LENGTH_REGEX.match(" ".join(msg[2:4]).lower())
        if r:
            number = float(r.group("number"))
            if number <= 0: return
            scale = r.group("scale").rstrip("s")
            td = None
            
            if scale == "second":
                td = datetime.timedelta(seconds=number)
            elif scale == "minute":
                td = datetime.timedelta(minutes=number)
            elif scale == "hour":
                td = datetime.timedelta(hours=number)
            elif scale == "day":
                td = datetime.timedelta(days=number)
            elif scale == "week":
                td = datetime.timedelta(weeks=number)
            elif scale == "month":
                td = datetime.timedelta(days=number * 30)
            elif scale == "year":
                td = datetime.timedelta(weeks=number * 52)
            
            now = datetime.datetime.now().strftime(TIME_FORMAT)
            expires = (datetime.datetime.now() + td).strftime(TIME_FORMAT)
        else:
            now = datetime.datetime.now().strftime(TIME_FORMAT)
            expires = now + datetime.timedelta(days=3652.4)

        f = open(file, "r")
        lines = f.readlines()
        f.close()
        if id in self.voteban:
            for searchID in lines:
                if searchID.startswith("#"): continue
                elif id != int(searchID.split(None, 1)[0]): continue
                words = searchID.split(" ")
                timeEnd = " ".join(words[3:5])
                banEnd = datetime.datetime.strptime(timeEnd, TIME_FORMAT)
                newEnd = datetime.datetime.strptime(expires, TIME_FORMAT)

                if (banEnd - newEnd).total_seconds() > 0:
                    player.tell("^2{} ^3 is already vote banned for longer. Use ^2!votebanlist".format(messageName))
                    return minqlx.RET_STOP_EVENT
                else:
                    h = open(file, "w")
                    for line in lines:
                        if line[0] == "#":
                            h.write(line)
                        elif id != int(line.split(None, 1)[0]):
                            h.write(line)
                        else:
                            h.write("{} {} {} {}\n".format(str(id), now, newEnd, target_player))
                    h.close()
                    player.tell("^2{}^3's ban time has been updated in the Vote Ban list.".format(messageName))
                    return minqlx.RET_STOP_EVENT

        else:
            newEnd = datetime.datetime.strptime(expires, TIME_FORMAT)
            for searchID in lines:
                if searchID.startswith("#"): continue
                elif id == int(searchID.split(None, 1)[0]):
                    h = open(file, "w")
                    for line in lines:
                        if line[0] == "#":
                            h.write(line)
                        elif id != int(line.split(None, 1)[0]):
                            h.write(line)
                        else:
                            h.write("{} {} {} {}\n".format(str(id), now, newEnd, target_player))
                    h.close()
                    player.tell("^2{}^3 has been added to the Vote Ban list.".format(messageName))
                    return minqlx.RET_STOP_EVENT

            h = open(file, "a")
            h.write("{} {} {} {}\n".format(str(id), now, newEnd, target_player))
            h.close()
            self.voteban.append(id)
            player.tell("^2{}^3 has been added to the Vote Ban list.".format(messageName))
        return minqlx.RET_STOP_EVENT

    # Removes the desired player from the vote ban list
    def cmd_voteUnBan(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=<^2player id^7|^2steam id^7>")
            return minqlx.RET_STOP_EVENT

        file = self.get_cvar("fs_homepath") + "/voteban.txt"
        try:
            with open(file) as test:
                pass
        except:
            player.tell("^3No one is vote banned on this server.")
            return minqlx.RET_STOP_EVENT

        target_player = False

        # Checks to see if client_id or steam_id was used
        try:
            id = int(msg[1])
            if 0 <= id <= 63:
                target_player = self.player(id)
                id = int(target_player.steam_id)
        except ValueError:
            player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
            return minqlx.RET_STOP_EVENT
        except minqlx.NonexistentPlayerError:
            player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
            return minqlx.RET_STOP_EVENT
        if len(str(id)) != 17:
            player.tell("^3The STEAM ID given needs to be 17 digits in length.")
            return minqlx.RET_STOP_EVENT

        if target_player:
            messageName = target_player
        else:
            messageName = str(id)

        # Opens the vote ban list file and removes the identified player.
        f = open(file, "r")
        lines = f.readlines()
        f.close()
        for searchID in lines:
            if searchID.startswith("#"): continue
            if id == int(searchID.split(None, 1)[0]):
                h = open(file, "w")
                for line in lines:
                    if line[0] == "#":
                        h.write(line)
                    elif id != int(line.split(None, 1)[0]):
                        h.write(line)
                h.close()
                if id in self.voteban:
                    self.voteban.remove(id)
                player.tell("^2{}^3 has been deleted from the Vote Ban list.".format(messageName))
                return minqlx.RET_STOP_EVENT

        player.tell("^2{}^3 is not on the Vote Ban list.".format(messageName))
        return minqlx.RET_STOP_EVENT

    # List players in the voteban file
    def cmd_voteBanList(self, player, msg, channel):
        player_list = self.players()
        if not player_list:
            player.tell("There are no players connected at the moment.")

        file = self.get_cvar("fs_homepath") + "/voteban.txt"
        list = "^5VoteBan List^7: If Active ^2'EndTime' ^7is in ^2Green\n"

        try:
            f = open(file, "r")
            g = f.readlines()
            f.close()
        except:
            player.tell("^3A vote ban list has not been made on this server yet.")
            return minqlx.RET_STOP_EVENT

        for line in g:
            if line.startswith("#"): continue
            foundName = False
            words = line.split(" ")
            id = words[0]
            for p in player_list:
                if int(id) == p.steam_id:
                    foundName = p.name
            endTime = " ".join(words[3:5])
            banEnd = datetime.datetime.strptime(endTime, TIME_FORMAT)
            if (banEnd - datetime.datetime.now()).total_seconds() >= 0:
                color = "^2EndTime"
            else:
                color = "^7EndTime"
            if not foundName:
                foundName = " ".join(words[5:]).strip("\n")

            if foundName:
                list += " ^7SteamID ^1{} {} ^1{}^7: ^3{}\n".format(id, color, endTime, foundName)
            else:
                list += " ^7SteamID ^1{} {} ^1{}^7: ^3No Name saved\n".format(id, color, endTime)

        player.tell(list[:-1])
        return minqlx.RET_STOP_EVENT