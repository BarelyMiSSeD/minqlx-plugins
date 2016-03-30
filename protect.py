# protect.py is a plugin for minqlx to:
# -protect selected players from being kicked using a callvote, if enabled
# -protect from mapvoting during an active match, if enabled
# -allow any player, even those on the protected list, to be put to spectator if the AFK vote passes, if enabled.
# created by BarelyMiSSeD on 11-10-15
# 
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
qlx_protectMapVoting  "1" - Enabling does not allow map voting during match play but does not effect map voting during warm-up. ("1" on, "0" off)
qlx_protectAfkVoting  "1" - Enabling will allow players to be voted into spectator. ("1" on, "0" off)
qlx_protectJoinMapMessage "0" - Sends join message to players if map voting protection is enabled. ("1" on, "0" off)
qlx_protectJoinAfkMessage "1" - Sends join message to players if voting players to spectator is enabled. ("1" on, "0" off)
qlx_protectPermissionLevel "5" - Sets the lowest level bot permission level to  automatically protect
qlx_protectMuteVoting "1" - Allows voting muting and unmuting of a player. ("1" on, "0" off)
qlx_protectJoinMuteVoting "1" - Sends join message to players if mute voting is enabled. ("1" on, "0" off)
qlx_protectAdminLevel "5" - Sets the minqlx server permission level needed to add/del/list the protect list, and display the protect.py version number.
qlx_protectPassLevel "5" - Sets the minqlx server permission level needed to set/unset the server join password.
qlx_protectFTS "5" - Sets the minqlx server permisson level needed to force teamsize.
"""

import minqlx
import re
import threading
import requests
import os

VERSION = "v1.06"
PROTECT_FILE = "protect.txt"

class protect(minqlx.Plugin):
    def __init__(self):
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)
        self.add_hook("player_loaded", self.player_loaded)

        # Cvars.
        self.set_cvar_once("qlx_protectMapVoting", "1")
        self.set_cvar_once("qlx_protectJoinMapMessage", "0")
        self.set_cvar_once("qlx_protectAfkVoting", "1")
        self.set_cvar_once("qlx_protectJoinAfkMessage", "1")
        self.set_cvar_once("qlx_protectPermissionLevel", "5")
        self.set_cvar_once("qlx_protectMuteVoting", "1")
        self.set_cvar_once("qlx_protectJoinMuteVoting", "1")
        self.set_cvar_once("qlx_protectAdminLevel", "5")
        self.set_cvar_once("qlx_protectPassLevel", "5")
        self.set_cvar_once("qlx_protectFTS", "5")

        self.protectPermission = self.get_cvar("qlx_protectPermissionLevel")
        self.mapProtect = self.get_cvar("qlx_protectMapVoting", bool)

        # Commands: permission level is set using some of the Cvars. See the Cvars descrition at the top of the file.
        self.add_command("protect", self.cmd_protect, int(self.get_cvar("qlx_protectAdminLevel")), usage="add|del|check|list <player id|steam id> |name|")
        self.add_command(("reload_protect", "load_protect"), self.cmd_loadProtects, int(self.get_cvar("qlx_protectAdminLevel")))
        self.add_command("setpass", self.cmd_setpass, int(self.get_cvar("qlx_protectPassLevel")))
        self.add_command("unsetpass", self.cmd_unsetpass, int(self.get_cvar("qlx_protectPassLevel")))
        self.add_command(("forcets", "forceteamsize"), self.teamsize_force, int(self.get_cvar("qlx_protectFTS")), usage="<wanted_teamsize>")
        self.add_command(("protectversion", "protect_version"), self.protect_version, int(self.get_cvar("qlx_protectAdminLevel")))
        self.add_command("protectlist", self.cmd_protectList, 5) # command for testing purposes
        
        # Opens Protect list container
        self.protect = []

        # Loads the protect list.
        self.cmd_loadProtects()

    # protect.py version checker. Thanks to iouonegirl for most of this section's code.
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

    def protect_version(self, player, msg, channel):
        self.check_version(channel=channel)

    # Player Join actions. Version checker and join messages.
    @minqlx.delay(4)
    def player_loaded(self, player):
        if player.steam_id == minqlx.owner():
            self.check_version(player=player)
        if self.get_cvar("qlx_protectJoinMapMessage", bool) and self.mapProtect:
            player.tell("^3Map voting during an active match is disabled on this server.")
        if self.get_cvar("qlx_protectJoinAfkMessage", bool) and  self.get_cvar("qlx_protectAfkVoting", bool) or self.get_cvar("qlx_protectJoinMuteVoting", bool) and  self.get_cvar("qlx_protectMuteVoting", bool):
                if self.get_cvar("qlx_protectJoinAfkMessage", bool) and self.get_cvar("qlx_protectJoinMuteVoting", bool):
                    player.tell("^3To vote someone to ^1Spectator ^3use ^4/cv afk <client id>^3 or"
                            "^4/cv spectate <client id>^3. To ^1Mute ^3someone use ^4/cv mute <client id>^3."
                            "To ^1UnMute ^3use ^4/cv unmute <client id>^3. Use ^4/players^3 in console to get client IDs.")
                elif self.get_cvar("qlx_protectJoinAfkMessage", bool):
                    player.tell("^3To vote someone to ^1Spectator ^3use ^4/cv afk <client id>^3 or"
                            "^4/cv spectate <client id>^3. Use ^4/players^3 in console to get client IDs.")
                elif self.get_cvar("qlx_protectJoinMuteVoting", bool):
                    player.tell("^3To ^1Mute ^3someone use ^4/cv mute <client id>."
                            "To ^1UnMute ^3use ^4/cv unmute <client id>. Use ^4/players^3 in console to get client IDs.")

    # Handles votes called: Kick protection, Map voting rejection during active matches, AFK voting, and Mute/UnMute voting.
    def handle_vote_called(self, caller, vote, args):
        # Map Voting
        vote = vote.lower()
        if (vote == "map" or vote == "nextmap" or vote == "map_restart") and self.mapProtect and self.game.state == "in_progress":
            caller.tell("^3Map voting is not allowed during an active match")
            return minqlx.RET_STOP_ALL
        # Kick Voting
        elif vote == "kick" or vote == "clientkick":
            try:
                client_id = int(args)
                target_player = self.player(client_id)
            except ValueError:
                target_player = self.player(args)
            ident = target_player.steam_id
            perm = self.db.get_permission(ident)
            if ident == minqlx.owner():
                caller.tell("^2That's my master! I won't let this vote pass.")
                return minqlx.RET_STOP_ALL
            elif int(perm) >= int(self.protectPermission):
                caller.tell("^2That player is too important on this server and can't be kicked.")
                return minqlx.RET_STOP_ALL
            elif ident in self.protect:
                caller.tell("^3That player is in the ^1kick protect^3 list.")
                return minqlx.RET_STOP_ALL
        # Voting people to Spectator
        elif vote == "afk" or vote == "spectate":
            if not self.get_cvar("qlx_protectAfkVoting", bool):
                caller.tell("^3Voting players to spectator is not enabled on this server.")
                return minqlx.RET_STOP_ALL
            try:
                player_name = self.player(int(args)).clean_name
                player_id = self.player(int(args)).id
            except:
                caller.tell("^1Invalid ID.^7 Use a client ID from the ^2/players^7 command.")
                return minqlx.RET_STOP_ALL

            if self.player(int(args)).team == "spectator":
                caller.tell("That player is already in the spectators.")
                return minqlx.RET_STOP_ALL
            self.callvote("put {} spec".format(player_id), "Move {} to spectate?".format(player_name))
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL
        # Voting to mute people
        elif vote == "mute" or vote == "silence":
            if not self.get_cvar("qlx_protectMuteVoting", bool):
                caller.tell("^3Voting to mute players is not enabled on this server.")
                return minqlx.RET_STOP_ALL
            try:
                player_name = self.player(int(args)).clean_name
                player_id = self.player(int(args)).id
            except:
                caller.tell("^1Invalid ID.^7 Use a client ID from the ^2/players^7 command.")
                return minqlx.RET_STOP_ALL
            ident = self.player(int(args)).steam_id
            perm = self.db.get_permission(ident)
            if ident == minqlx.owner():
                caller.tell("^2That's my master! I won't let this vote pass.")
                return minqlx.RET_STOP_ALL
            elif int(perm) >= int(self.protectPermission):
                caller.tell("^2That player is too important on this server and can't be muted.")
                return minqlx.RET_STOP_ALL
            self.callvote("mute {}".format(player_id), "Mute {}?".format(player_name))
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL
        # Voting to unMute people
        elif vote == "unmute" or vote == "unsilence":
            if not self.get_cvar("qlx_protectMuteVoting", bool):
                caller.tell("^3Voting to mute/unmute players is not enabled on this server.")
                return minqlx.RET_STOP_ALL
            try:
                player_name = self.player(int(args)).clean_name
                player_id = self.player(int(args)).id
            except:
                caller.tell("^1Invalid ID.^7 Use a client ID from the ^2/players^7 command.")
                return minqlx.RET_STOP_ALL
            if int(caller.id) == int(player_id):
                caller.tell("^3Sorry, you cannot callvote to unmute yourself.")
                return minqlx.RET_STOP_ALL
            self.callvote("unmute {}".format(player_id), "UnMute {}?".format(player_name))
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL

    # Checks for a protect.txt file and loads the entries if the file exists. Creates one if it doesn't.
    def cmd_loadProtects(self, player=None, msg=None, channel=None):
        try:
            f = open(os.path.join(self.get_cvar("fs_homepath"), PROTECT_FILE), "r")
            lines = f.readlines()
            f.close()
            tempList = []
            for id in lines:
                if id.startswith("#"): continue
                try:
                    tempList.append(int(id.split(None, 1)[0].strip('\n')))
                except:
                    continue
            self.protect = tempList
            if player:
                player.tell("^3The protect list has been reloaded. ^1!protect list ^3 to see current load.")
        except IOError as e:
            try:
                m = open(os.path.join(self.get_cvar("fs_homepath"), PROTECT_FILE), "w")
                m.write("# This is a commented line because it starts with a '#'\n")
                m.write("# Enter every protect SteamID and name on a newline, format: SteamID Name\n")
                m.write("# The NAME is for a mental reference and may contain spaces.\n")
                m.write("# NAME will be added automatically if the protection is added with a client id when the player is connected to the server.\n")
                m.write("{} ServerOwner\n".format(minqlx.owner()))
                m.close()
                tempList = []
                tempList.append(int(minqlx.owner()))
                self.protect = tempList
                if player:
                    player.tell("^3No ^1Protect^3 list was found so one was created and the server owner was added.")
            except:
                if player:
                    player.tell("^1Error ^3reading and/or creating the Protect list: {}".format(e))
        except Exception as e:
            if player:
                player.tell("^1Error ^3reading the Protect list: {}".format(e))
        return minqlx.RET_STOP_EVENT

    # The PROTECT command: add, del, check, and list people.
    def cmd_protect(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> |name|")
            return minqlx.RET_STOP_EVENT

        file = os.path.join(self.get_cvar("fs_homepath"), PROTECT_FILE)
        try:
            with open(file) as test:
                pass
        except Exception as e:
            player.tell("^1Error ^3reading the Protect list file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        action = msg[1].lower()
        target_player = False

        # Executes if msg begins with "!protect add"
        if action == "add":
            if len(msg) < 3:
                player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> ^7<^2name^7>")
                return minqlx.RET_STOP_EVENT
            try:
                id = int(msg[2])
                if 0 <= id <= 63:
                    try:
                        target_player = self.player(id)
                    except minqlx.NonexistentPlayerError:
                        player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                        return minqlx.RET_STOP_EVENT
                    if not target_player:
                        player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                        return minqlx.RET_STOP_EVENT
                    id = int(target_player.steam_id)
                elif id < 0:
                    player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> ^7<^2name^7>")
                    return minqlx.RET_STOP_EVENT
                elif len(str(id)) != 17:
                    player.tell("^3The STEAM ID given needs to be 17 digits in length.")
                    return minqlx.RET_STOP_EVENT
            except ValueError:
                player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT

            if target_player:
                message = "{} {}".format(id, target_player).split()
            else:
                target_player = " ".join(msg[3:])
                message = msg[2:]

            if id in self.protect:
                player.tell("^2{}^3 is already in the Protect list.".format(target_player))
                self.updateLine(player=player, addName=message)
                return minqlx.RET_STOP_EVENT

            if not target_player:
                target_player = "Name not supplied"

            h = open(file, "a")
            h.write(str(id) + " " + str(target_player) + "\n")
            h.close()
            self.protect.append(id)
            player.tell("^2{}^3 has been added to the Protect list.".format(target_player))
            return minqlx.RET_STOP_EVENT

        # Executes if msg begins with "!protect del"
        elif action == "del":
            if len(msg) < 3:
                player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> |name|")
                return minqlx.RET_STOP_EVENT
            try:
                id = int(msg[2])
                if 0 <= id <= 63:
                    try:
                        target_player = self.player(id)
                    except minqlx.NonexistentPlayerError:
                        player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                        return minqlx.RET_STOP_EVENT
                    if not target_player:
                        player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                        return minqlx.RET_STOP_EVENT
                    id = int(target_player.steam_id)
                elif id < 0:
                    player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> |name|")
                    return minqlx.RET_STOP_EVENT
                elif len(str(id)) != 17:
                    player.tell("^3The STEAM ID given needs to be 17 digits in length.")
                    return minqlx.RET_STOP_EVENT
            except ValueError:
                player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT

            f = open(file, "r")
            lines = f.readlines()
            f.close()
            for search_id in lines:
                if search_id.startswith("#"): continue
                if id == int(search_id.split(None, 1)[0]):
                    h = open(file, "w")
                    for line in lines:
                        if line[0] == "#":
                            h.write(line)
                        elif id != int(line.split(None, 1)[0]):
                            h.write(line)
                    h.close()
                    if id in self.protect:
                        self.protect.remove(id)
                    if target_player:
                        player.tell("^2{}^3 has been deleted from the Protect list.".format(target_player))
                    else:
                        player.tell("^2{}^3 has been deleted from the Protect list.".format(id))
                    return minqlx.RET_STOP_EVENT
            if target_player:
                player.tell("^2{}^3 is not in the protect list.".format(target_player))
            else:
                player.tell("^2{}^3 is not in the protect list.".format(id))
            return minqlx.RET_STOP_EVENT

        # Executes if msg begins with "!protect check"
        elif action == "check":
            if len(msg) < 3:
                player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> |name|")
                return minqlx.RET_STOP_EVENT
            try:
                id = int(msg[2])
                if 0 <= id <= 63:
                    try:
                        target_player = self.player(id)
                    except minqlx.NonexistentPlayerError:
                        player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                        return minqlx.RET_STOP_EVENT
                    if not target_player:
                        player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                        return minqlx.RET_STOP_EVENT
                    id = int(target_player.steam_id)
                elif id < 0:
                    player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> |name|")
                    return minqlx.RET_STOP_EVENT
                elif len(str(id)) != 17:
                    player.tell("^3The STEAM ID given needs to be 17 digits in length.")
                    return minqlx.RET_STOP_EVENT
            except ValueError:
                player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT

            if id in self.protect:
                if target_player:
                    player.tell("^2{}^3 is in the Protect list.".format(target_player))
                else:
                    player.tell("^2{}^3 is in the protect list".format(id))
                return minqlx.RET_STOP_EVENT
            else:
                if target_player:
                    player.tell("^2{}^3 is ^1NOT^3 in the Protect list.".format(target_player))
                else:
                    player.tell("^2{}^3 is ^1NOT^3 in the Protect List.".format(id))
                return minqlx.RET_STOP_EVENT

        # Executes if msg begins with "!protect list"
        elif action == "list":
            player_list = self.players()
            if not player_list:
                player.tell("There are no players connected at the moment.")
            list = "^5Protect List:\n"
            f = open(file, "r")
            lines = f.readlines()
            f.close()
            for line in lines:
                if line.startswith("#"): continue
                line = line.split(" ")
                id = line[0].strip("\n")
                foundName = False
                savedName = False
                for p in player_list:
                    if int(id) == p.steam_id:
                        foundName = p.name
                if not foundName:
                    savedName = " ".join(line[1:]).strip("\n")

                if foundName:
                    list += "  ^7SteamID ^1{} ^7: ^4{}\n".format(id, foundName)
                elif savedName:
                    list += "  ^7SteamID ^1{} ^7: ^4{} ^7: ^3Player not connected\n".format(id, savedName)
                else:
                    list += "  ^7SteamID ^1{} ^7: ^4No Name saved ^7: ^3Player not connected\n".format(id)

            player.tell(list[:-1])
            return minqlx.RET_STOP_EVENT
        else:
            player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> |name|")
            return minqlx.RET_STOP_EVENT

    # Updates the protect.txt file with a player name if one was not previously saved when player was originally added.
    def updateLine(self, player=None, addName=None):
        if len(addName) > 1:
            file = os.path.join(self.get_cvar("fs_homepath"), PROTECT_FILE)
            f = open(file, "r")
            lines = f.readlines()
            f.close()
            id = int(addName[0])
            for checkID in lines:
                check = checkID.split()
                if id == int(check[0]) and len(check) == 1:
                    h = open(file, "w")
                    for line in lines:
                        if line[0] == "#":
                            h.write(line)
                        elif id == int(line.split(None, 1)[0]):
                            h.write(" ".join(addName[0:]) + "\n")
                        else:
                            h.write(line)
                    h.close()
                    return minqlx.RET_STOP_EVENT
        return minqlx.RET_STOP_EVENT

    # Command used for testing: shows the contents of the self.protect string used to protect players from being kicked.
    def cmd_protectList(self, player, msg, channel):
        player.tell("List: " + str(self.protect))
        return minqlx.RET_STOP_EVENT

    # Sets a server join password
    def cmd_setpass(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=^2<password>")
            return minqlx.RET_STOP_EVENT

        password = str(msg[1])
        minqlx.console_command("set g_password {}".format(password))
        player.tell("^3Server join password is set to ^1{}.".format(password))
        return minqlx.RET_STOP_EVENT

    # Clears the server join password
    def cmd_unsetpass(self, player, msg, channel):
        minqlx.console_command('set g_password ""')
        player.tell("^3Server join password has been cleared.")
        return minqlx.RET_STOP_EVENT

    # Forces the teamsize to the desired size, puts all players to spectate if needed to set the teamsize.
    def teamsize_force(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            wanted_teamsize = int(msg[1])
        except ValueError:
            player.tell("^1Unintelligible size.")
            return minqlx.RET_STOP_EVENT

        teams = self.teams()
        teamsize = self.get_cvar("teamsize")
        if int(teamsize) == wanted_teamsize:
            player.tell("^4The teamsize is already {}.".format(teamsize))
            return minqlx.RET_STOP_EVENT

        red_teamsize = len(teams["red"])
        blue_teamsize = len(teams["blue"])
        if int(red_teamsize) <= wanted_teamsize and int(blue_teamsize) <= wanted_teamsize:
            self.game.teamsize = wanted_teamsize
            self.msg("^4Server: ^7The teamsize was set to ^1{}^7.".format(wanted_teamsize))
        else:
            for client in teams["red"]:
                client.put("spectator")
            for client in teams["blue"]:
                client.put("spectator")
            self.game.teamsize = wanted_teamsize
            self.msg("^4Server: ^7The teamsize was set to ^1{}^7, players were put to spectator to allow the change.".format(wanted_teamsize))
        return minqlx.RET_STOP_EVENT